import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from gepl_auction_platform_backend.core.models import Players
from gepl_auction_platform_backend.core.models import Teams
from gepl_auction_platform_backend.users.models import User


def create_response(player_list):
    return list(player_list)


def update_player_obj(player_id, bid, team_id):
    Players.objects.filter(id=player_id).update(
        is_player_sold=True,
        team_id=team_id,
        shadow_base_price=bid,
    )


def update_team_obj(owner, budget):
    Teams.objects.filter(owner=owner).update(budget=budget)


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "auction_room"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Initialize shared state if not already done
        if not hasattr(self.channel_layer, "player_queue"):
            self.channel_layer.player_queue = []
            self.channel_layer.current_player = None
            self.channel_layer.highest_bid = None
            self.channel_layer.bidder_budgets = {}
            self.channel_layer.bidder_budgets2 = []
            self.channel_layer.timer_task = None

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "START_AUCTION":
            category = data.get("category")
            async for team in Teams.objects.all().prefetch_related("owner"):
                self.channel_layer.bidder_budgets[team.owner.username] = team.budget
                self.channel_layer.bidder_budgets2.append(
                    {
                        "bidder": team.owner.username,
                        "budget": team.budget,
                    },
                )
            player_list = Players.objects.filter(category=category).values()
            self.channel_layer.player_queue = await sync_to_async(create_response)(
                player_list,
            )
            await self.send_next_player()

        elif action == "place_bid":
            bid_amount = data.get("bid_amount")
            bidder = data.get("bidder")
            current_player = self.channel_layer.current_player
            bidder_budgets = self.channel_layer.bidder_budgets

            if (
                current_player
                and current_player.get("name")
                and bidder_budgets.get(bidder, 0) >= bid_amount
            ):
                obj = await Players.objects.aget(id=current_player.get("id"))
                obj.bid_amount = bid_amount
                obj.asave()
                self.channel_layer.highest_bid = {
                    "bid_amount": bid_amount,
                    "bidder": bidder,
                }
                self.channel_layer.bidder_budgets[bidder] -= bid_amount

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_bid",
                        "bid_amount": bid_amount,
                        "bidder": bidder,
                        "player": current_player["name"],
                        "player_id": current_player["id"],
                    },
                )
                await self.send_budget_update()
                await self.restart_bid_timer(20, sell=True)

    async def send_budget_update(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "budget_update",
                "budgets": self.channel_layer.bidder_budgets,
            },
        )

    async def send_next_player(self):
        if self.channel_layer.timer_task:
            self.channel_layer.timer_task.cancel()

        if self.channel_layer.player_queue:
            self.channel_layer.current_player = self.channel_layer.player_queue.pop(0)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_player",
                    "player": self.channel_layer.current_player.get("name"),
                    "category": self.channel_layer.current_player.get("category"),
                    "player_id": self.channel_layer.current_player.get("id"),
                },
            )
            await self.restart_bid_timer(20, sell=False)
        else:
            await self.send(text_data=json.dumps({"type": "auction_complete"}))

    async def new_bid(self, event):
        await self.send(text_data=json.dumps(event))

    async def new_player(self, event):
        await self.send(text_data=json.dumps(event))

    async def budget_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def restart_bid_timer(self, seconds, sell):
        if self.channel_layer.timer_task:
            self.channel_layer.timer_task.cancel()

        self.channel_layer.timer_task = asyncio.create_task(
            self.start_bid_timer(seconds, sell),
        )

    async def start_bid_timer(self, seconds, sell):
        await asyncio.sleep(seconds)
        current_player = self.channel_layer.current_player
        highest_bid = self.channel_layer.highest_bid

        if sell and highest_bid and current_player:
            bidder_username = self.channel_layer.highest_bid["bidder"]
            user_obj = await User.objects.aget(username=highest_bid["bidder"])
            team_obj = await Teams.objects.aget(owner=user_obj.id)

            await sync_to_async(update_player_obj)(
                current_player["id"],
                highest_bid["bid_amount"],
                team_obj.id,
            )
            await sync_to_async(update_team_obj)(
                user_obj.id,
                self.channel_layer.bidder_budgets[bidder_username],
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_sold",
                    "player": current_player.get("name"),
                    "player_id": current_player.get("id"),
                    "bidder": highest_bid["bidder"],
                    "bid_amount": highest_bid["bid_amount"],
                },
            )
        elif current_player:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_unsold",
                    "player": current_player.get("name"),
                    "player_id": current_player.get("id"),
                },
            )
        await asyncio.sleep(5)
        await self.send_next_player()

    async def player_sold(self, event):
        await self.send(text_data=json.dumps(event))

    async def player_unsold(self, event):
        await self.send(text_data=json.dumps(event))

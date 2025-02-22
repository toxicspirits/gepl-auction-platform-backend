import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer


# Mock function to fetch players from the database based on category
def fetch_players_by_category(category):
    # Replace with actual DB queries
    all_players = [
        {"name": "Player 1", "category": "CATEGORY_A", "id": 1},
        {"name": "Player 2", "category": "CATEGORY_B", "id": 2},
        {"name": "Player 3", "category": "CATEGORY_C", "id": 3},
        {"name": "Player 4", "category": "CATEGORY_A", "id": 4},
        {"name": "Player 5", "category": "CATEGORY_A", "id": 5},
        {"name": "Player 6", "category": "CATEGORY_A", "id": 6},
        {"name": "Player 7", "category": "CATEGORY_A", "id": 7},
        {"name": "Player 8", "category": "CATEGORY_B", "id": 8},
        {"name": "Player 9", "category": "CATEGORY_B", "id": 9},
        {"name": "Player 10", "category": "CATEGORY_B", "id": 10},
        {"name": "Player 11", "category": "CATEGORY_B", "id": 11},
        {"name": "Player 12", "category": "CATEGORY_C", "id": 12},
        {"name": "Player 13", "category": "CATEGORY_C", "id": 13},
        {"name": "Player 14", "category": "CATEGORY_C", "id": 14},
        {"name": "Player 15", "category": "CATEGORY_C", "id": 15},
    ]
    # Filter players only from the selected category
    return [player for player in all_players if player["category"] == category]


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
            self.channel_layer.bidder_budgets = {"User1": 10000, "User2": 10000}
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
            self.channel_layer.player_queue = fetch_players_by_category(category)
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
        await self.send_next_player()

    async def player_sold(self, event):
        await self.send(text_data=json.dumps(event))

    async def player_unsold(self, event):
        await self.send(text_data=json.dumps(event))

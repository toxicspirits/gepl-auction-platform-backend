import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from gepl_auction_platform_backend.core.models import Players


class BiddingRoom(AsyncWebsocketConsumer):
    auction_timers = {}  # Store timers for each auction
    auction_timers_2 = {}
    current_player_index = 0
    bid_number = 1
    current_category = None
    current_player = None
    category_list = [
        "CATEGORY_A",
        "CATEGORY_B",
        "CATEGORY_C",
    ]

    def fetch_player(self, category, current_player_index):
        b = (
            Players.objects.filter(category=category)
            .values()
            .values_list("name", "role", "base_price")
        )
        return list(b)[current_player_index]

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        category = self.category_list[0]
        if action == "start_bidding":
            b = await sync_to_async(self.fetch_player)(
                category=category,
                current_player_index=self.current_player_index,
            )
            self.category = category
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player_queue",
                    "player": b,
                    "current_player": self.current_player_index,
                },
            )

            if self.category not in self.auction_timers:
                self.auction_timers[self.category] = asyncio.create_task(
                    self.start_bid_timer(1, self.category),
                )

        if action == "place_bid":
            bid_amount = data["bid_amount"]
            bidder = data["bidder"]
            team = data["team"]
            category = data["category"]
            # Broadcast bid to all users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_bid",
                    "bid_amount": bid_amount,
                    "bidder": bidder,
                    "team": team,
                    "bid_number": self.bid_number + 1,
                    "category": category,
                },
            )

            # Start bid timer
            if team not in self.auction_timers:
                self.auction_timers[team] = asyncio.create_task(
                    self.start_bid_timer(team, category),
                )

    async def new_bid(self, event):
        await self.send(text_data=json.dumps(event))

    async def player_queue(self, event):
        await self.send(text_data=json.dumps(event))

    async def start_bid_timer(self, team, category):
        await asyncio.sleep(20)  # 10 seconds timer
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "bid_time_up",
                "team": team,
            },
        )

        self.auction_timers.pop(team, None)
        self.current_player_index = self.current_player_index + 1
        self.bid_number = 0

        b = await sync_to_async(self.fetch_player)(
            category=category,
            current_player_index=self.current_player_index,
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "player_queue",
                "players": b,
                "current_player": self.current_player_index + 1,
            },
        )

        self.auction_timers_2.pop(category, None)

    async def bid_time_up(self, event):
        await self.send(text_data=json.dumps(event))

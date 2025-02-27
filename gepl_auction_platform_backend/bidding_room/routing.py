from django.urls import re_path

from . import bidding_v3

websocket_urlpatterns = [
    re_path(
        r"ws/bidding_room/(?P<room_name>\w+)$",
        bidding_v3.AuctionConsumer.as_asgi(),
    ),
]

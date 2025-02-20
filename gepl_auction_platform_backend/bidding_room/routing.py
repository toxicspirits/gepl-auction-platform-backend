from django.urls import re_path

from . import bidding

websocket_urlpatterns = [
    re_path(r"ws/bidding_room/(?P<room_name>\w+)$", bidding.BiddingRoom.as_asgi()),
]

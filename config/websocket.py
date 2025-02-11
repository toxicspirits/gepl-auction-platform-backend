import json

from gepl_auction_platform_backend.core.models import Players


async def websocket_application(scope, receive, send):
    while True:
        event = await receive()

        if event["type"] == "websocket.connect":
            await send({"type": "websocket.accept"})

        if event["type"] == "websocket.disconnect":
            break

        if event["type"] == "websocket.receive":
            event = json.loads(event["text"])
            if event["event_type"] == "UPDATE_BID":
                b = await Players.objects.aget(pk=1)
                b.base_price = event["bid"]
                await b.asave()
                await send({"type": "websocket.send", "text": json.dumps(event)})

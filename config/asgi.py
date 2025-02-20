# ruff: noqa
"""
ASGI config for gepl-auction-platform-backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""

# import os
# import sys
# from pathlib import Path
#
# from django.core.asgi import get_asgi_application
#
# # This allows easy placement of apps within the interior
# # gepl_auction_platform_backend directory.
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
# sys.path.append(str(BASE_DIR / "gepl_auction_platform_backend"))
#
# # If DJANGO_SETTINGS_MODULE is unset, default to the local settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
#
# # This application object is used by any ASGI server configured to use this file.
# django_application = get_asgi_application()
# # Apply ASGI middleware here.
# # from helloworld.asgi import HelloWorldApplication
# # application = HelloWorldApplication(application)
#
# # Import websocket application here, so apps from django_application are loaded first
# from config.websocket import websocket_application
#
#
# async def application(scope, receive, send):
#     if scope["type"] == "http":
#         await django_application(scope, receive, send)
#     elif scope["type"] == "websocket":
#         await websocket_application(scope, receive, send)
#     else:
#         msg = f"Unknown scope type {scope['type']}"
#         raise NotImplementedError(msg)

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from gepl_auction_platform_backend.bidding_room.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        ),
    }
)

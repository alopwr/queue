"""
ASGI config for queueapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application

import que.websockets.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queueapp.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": SessionMiddlewareStack(URLRouter(que.websockets.routing.urls,)),
    }
)

"""
ASGI config for LibrSite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
from daphne import server
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import online_libr.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibrSite.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
           online_libr.routing.ws_chat_urlpatterns
        )
    )
})


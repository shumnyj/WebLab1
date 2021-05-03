from django.urls import re_path

from . import consumers

ws_chat_urlpatterns = [
    re_path(r'chat/$', consumers.ChatConsumer.as_asgi()),
]
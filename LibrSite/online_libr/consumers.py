import json
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from django.contrib.auth import models as auth_models
from .models import ChatUser, LibUser, Book


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'BookChat'  # % self.scope['url_route']['kwargs']['room_name']
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        if isinstance(self.scope['user'], auth_models.User):        # no anon !
            ChatUser.objects.update_or_create(user=self.scope['user'])
            self.username = self.scope['user'].username
            self.accept()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': "- User %s joined chat" % self.username
                }
            )
            # possible to make send user + id -> check and update dom from javascript
        else:
            self.accept()
            self.send(text_data=json.dumps({
                'message': "Login first!!!"
            }))
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "- User %s left" % self.username
            }
        )
        ChatUser.objects.filter(user=self.scope['user']).delete()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':  message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
        }))
        # Check if it was kick message
        try:
            kick_user = event['kick_username']
            if self.username == kick_user:
                print('got kick')
                self.close()
        except KeyError:
            pass


class TasksConsumer(WebsocketConsumer):
    room_group_name = 'TasksListen'

    def connect(self):
        self.room_group_name = 'TasksListen'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # print(str(self.scope['user']))
        if isinstance(self.scope['user'], auth_models.User):
            self.username = self.scope['user'].username
        else:
            self.username = "worker %d" % random.randrange(1, 100)  # not bothering with unique names
        self.accept()
        """        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'task_message',
                'task': "Connected",
                'note': "test",
            }
        )"""

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['task']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            text_data_json
        )

    def task_message(self, event):
        pack = {"task": None, "args": None, "result": None, "finished": None, "task_id": None, "note": None}
        for field in event.keys():
            if field != "type":
                pack[field] = event[field]
        self.send(text_data=json.dumps(pack))

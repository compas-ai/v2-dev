from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.utils import timezone

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Get chat community from URL
        self.chat_community = self.scope['url_route']['kwargs']['chat_community']
        self.room_group_name = f"public_room_{self.chat_community}"
        

        print(self.room_group_name)
        print(self.channel_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        dp = text_data_json['dp']
        images = text_data_json['images']
        id= text_data_json['id']
        name = text_data_json['name']
        mode = text_data_json['mode']
        timestamp = timezone.now().strftime("%I:%M %p")

        print(mode)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'dp': dp,
                'images': images,
                'id': id,
                'timestamp': timestamp,
                'mode': mode,
                'name': name 
            }

           
        )
        print("sent")

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        dp = event['dp']
        images = event['images']
        id=event['id']
        timestamp = event['timestamp']
        mode = event['mode']
        name = event['name']


        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'dp': dp,
            'images': images,
            'id': id,
            'timestamp': timestamp,
            'mode': mode,
            'name': name 
        }))

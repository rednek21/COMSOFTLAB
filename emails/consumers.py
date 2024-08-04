import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'emails'
        self.room_group_name = 'emails_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def email_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
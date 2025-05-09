import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Conversation

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        try:
            self.conversation_id = int(self.scope['url_route']['kwargs']['conversation_id'])
        except ValueError:
            await self.close() # Invalid conversation_id format
            return
            
        self.conversation_group_name = f'chat_{self.conversation_id}'

        # Check if the user is a participant in this conversation
        is_participant = await self.is_user_participant(self.user, self.conversation_id)
        if not is_participant:
            await self.close() # Deny connection
            return

        # Join room group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.user or not self.user.is_authenticated:
            return # Should be handled by connect, but good for safety

        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get('message')
        except json.JSONDecodeError:
            # Handle malformed JSON
            return

        if not message_content or not isinstance(message_content, str):
            return # Ignore empty or invalid messages

        # Save message to database
        message_obj = await self.save_message(self.user, self.conversation_id, message_content)

        if message_obj:
            # Send message to room group
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'chat.message', # Convention: app_label.message_type
                    'message_id': message_obj.id,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username, # Or other display name
                    'content': message_obj.content,
                    'timestamp': message_obj.created_at.isoformat()
                }
            )

    # Handler for messages from the group (e.g., chat.message type)
    async def chat_message(self, event):
        # Send message to WebSocket (client)
        await self.send(text_data=json.dumps(event)) # Send the whole event data

    @database_sync_to_async
    def is_user_participant(self, user, conversation_id):
        try:
            return Conversation.objects.filter(id=conversation_id, participants=user).exists()
        except Conversation.DoesNotExist: # Should not happen with .exists() but good practice
            return False

    @database_sync_to_async
    def save_message(self, user, conversation_id, content):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            # Double check participant status before saving, though connect should handle it
            if not conversation.participants.filter(id=user.id).exists():
                # Log this, as it implies a logic error or bypass
                print(f"Warning: User {user.id} tried to send message to conversation {conversation_id} they are not part of.")
                return None
            
            message = Message.objects.create(
                conversation=conversation,
                sender=user,
                content=content
            )
            return message
        except Conversation.DoesNotExist:
            # Log this error
            print(f"Error: Conversation {conversation_id} not found when trying to save message.")
            return None
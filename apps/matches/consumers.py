from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth.models import AnonymousUser
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser()) # Получаем пользователя из scope
        if self.user.is_anonymous:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']

        is_participant = await self.check_participation(self.user, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f'chat_{self.conversation_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def check_participation(self, user, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.participants.filter(id=user.id).exists()
        except Conversation.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        # sender_id должен приходить от клиента (chat.js)
        # Убедитесь, что клиент (chat.js) отправляет sender_id
        # sender_id = text_data_json.get('sender_id') # Если клиент шлет

        # Лучше использовать self.user, установленный при connect
        if self.user.is_anonymous:
            return # Не обрабатывать сообщения от анонимов

        # Сохраняем сообщение в БД
        message_db = await self.save_message_to_db(self.user, self.conversation_id, message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_db.content, # Используем сохраненное содержимое
                'sender_id': str(self.user.id), # Отправитель - текущий пользователь WebSocket
                'sender_name': self.user.first_name or self.user.username,
                'timestamp': message_db.created_at.isoformat() # ISO формат для JS
            }
        )

    @database_sync_to_async
    def save_message_to_db(self, sender_user, conversation_id, content):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            # Убеждаемся, что отправитель является участником беседы (дополнительная проверка)
            if not conversation.participants.filter(id=sender_user.id).exists():
                # Этого не должно происходить, если проверка в connect() работает
                raise Exception("Sender is not a participant of this conversation.")

            message = Message.objects.create(
                conversation=conversation,
                sender=sender_user,
                content=content
            )
            # Обновляем updated_at для беседы, чтобы она поднималась в списке
            conversation.save(update_fields=['updated_at'])
            return message
        except Conversation.DoesNotExist:
            # Обработка случая, если беседа не найдена
            raise Exception("Conversation not found during message save.")


    async def chat_message(self, event):
        # Эта функция просто отправляет данные клиенту
        await self.send(text_data=json.dumps({
            'content': event['message'], # 'message' здесь это event['message'] из group_send
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))
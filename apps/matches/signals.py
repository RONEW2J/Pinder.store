from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Message
from apps.notifications.models import Notification # Assuming this model exists and is appropriate

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Создание уведомления при получении нового сообщения"""
    if created: # Only on new messages
        conversation = instance.conversation
        message_sender = instance.sender

        # Determine the recipient(s) - the other participant(s) in the conversation
        participants = list(conversation.participants.all())
        
        recipient = None
        # For a 1-on-1 Tinder-style chat, there should be exactly two participants.
        if len(participants) == 2:
            if participants[0].id == message_sender.id:
                recipient = participants[1]
            else:
                recipient = participants[0]
        
        if recipient:
            title = f'New message from {message_sender.username}'
            message_content = instance.content[:50] + ('...' if len(instance.content) > 50 else '')
            
            # The link should point to the specific conversation.
            # You'll need a URL pattern named 'conversation_detail' in your 'matches' app's urls.py
            # or a relevant frontend route.
            try:
                chat_link = reverse('matches:conversation_detail', args=[conversation.id])
            except Exception: # Fallback if URL is not yet defined
                chat_link = f"/app/chat/{conversation.id}/" # Example frontend link

            Notification.objects.create(
                user=recipient,
                notification_type='chat_message', # Or a more generic type
                title=title,
                message=message_content,
                link=chat_link
            )
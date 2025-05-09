from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Match, Conversation, Message

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    """Basic user info for participants."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name'] # Add profile picture URL if available

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'created_at']
        read_only_fields = ['conversation', 'sender', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSimpleSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'updated_at', 'last_message']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSimpleSerializer(read_only=True)
    user2 = UserSimpleSerializer(read_only=True)
    # You might want to include the conversation ID directly if a match always has one
    conversation_id = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'created_at', 'conversation_id']

    def get_conversation_id(self, obj):
        # Assuming a conversation is created with every match
        conversation = Conversation.objects.filter(participants=obj.user1).filter(participants=obj.user2).first()
        return conversation.id if conversation else None
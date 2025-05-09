from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer

# Create your views here.

class MatchListView(generics.ListAPIView):
    """
    Lists all matches for the currently authenticated user.
    A match implies a conversation has been initiated.
    """
    serializer_class = MatchSerializer # Or ConversationSerializer if you prefer to list conversations directly
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Matches where the user is either user1 or user2
        return Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

class ConversationListView(generics.ListAPIView):
    """
    Lists all conversations for the currently authenticated user.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.conversations_participated.all().order_by('-updated_at')

class MessageListView(generics.ListAPIView):
    """
    Lists messages for a specific conversation.
    The user must be a participant in the conversation.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        # Ensure the user is part of this conversation before listing messages
        if Conversation.objects.filter(id=conversation_id, participants=self.request.user).exists():
            return Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
        return Message.objects.none() # Return empty queryset if user is not a participant

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists() and not Conversation.objects.filter(id=self.kwargs.get('conversation_id'), participants=request.user).exists():
             # Check if the conversation itself exists and if the user is a participant
            if not Conversation.objects.filter(id=self.kwargs.get('conversation_id')).exists():
                return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "You do not have permission to view messages for this conversation."}, status=status.HTTP_403_FORBIDDEN)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Note: The 'conversation_detail' URL used in signals.py might be a frontend route.
# If it's meant to be a backend API endpoint to fetch conversation details, you'd add a RetrieveAPIView here.
# For example:
class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' # or 'pk'

    def get_queryset(self):
        # Ensure user is a participant
        return super().get_queryset().filter(participants=self.request.user)

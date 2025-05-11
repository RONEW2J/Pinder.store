from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Match, Conversation, Message
from rest_framework.views import APIView
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer

class MatchListView(generics.ListAPIView):
    """
    Lists all matches for the currently authenticated user.
    A match implies a conversation has been initiated.
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
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
    
    _conversation_instance = None

    def get_conversation(self):
        if self._conversation_instance is None:
            conversation_id = self.kwargs.get('conversation_id')
            if not conversation_id:
                return None
                
            try:
                self._conversation_instance = Conversation.objects.get(
                    id=conversation_id,
                    participants=self.request.user
                )
            except Conversation.DoesNotExist:
                self._conversation_instance = None
                
        return self._conversation_instance

    def get_queryset(self):
        conversation = self.get_conversation()
        if conversation:
            return Message.objects.filter(
                conversation=conversation
            ).order_by('created_at')
        return Message.objects.none()

    def list(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_id')
        
        if not Conversation.objects.filter(id=conversation_id).exists():
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not self.get_conversation():
            return Response(
                {"detail": "You do not have permission to view messages for this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs)

class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().filter(participants=self.request.user)
    
class UnmatchView(APIView):
    def post(self, request, profile_id):
        match = get_object_or_404(
            Match.objects.filter(
                (Q(user1=request.user) & Q(user2_id=profile_id)) |
                (Q(user2=request.user) & Q(user1_id=profile_id))
            )
        )
        match.delete()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
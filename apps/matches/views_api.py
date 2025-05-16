from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
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
    
# In views_api.py
class UnmatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id): # Changed parameter name
        try:
            # Get User object directly by user_id
            user_to_unmatch = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        current_user = request.user
        # The rest of your logic for finding and deleting the match and conversation remains the same
        # as it correctly uses user objects (user1, user2).
        u1, u2 = (current_user, user_to_unmatch) if current_user.id < user_to_unmatch.id else (user_to_unmatch, current_user)

        match = get_object_or_404(Match, user1=u1, user2=u2)

        with transaction.atomic():
            if match.conversation:
                match.conversation.delete()
            match.delete()

        return Response({'status': 'success', 'message': 'Successfully unmatched.'}, status=status.HTTP_200_OK)
    
class SwipeActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, profile_id, action):
        if action not in ('like', 'pass'):
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_profile = get_object_or_404(Profile, pk=profile_id)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        current_user_profile = request.user.profile  # Or however you get the current user's profile

        try:
            with transaction.atomic():
                SwipeAction.objects.update_or_create(
                    swiper=request.user,  # Or swiper_profile=current_user_profile
                    profile=target_profile,
                    defaults={'action': action}
                )

                match_occurred = False
                conversation_id = None
                if action == 'like' and SwipeAction.objects.filter(
                    swiper=target_profile.user, profile=request.user.profile, action='like'
                ).exists():
                    match_occurred = True
                    match, conversation = Match.create_match_and_conversation(request.user, target_profile.user)
                    conversation_id = conversation.id

                response_data = {
                    'status': 'success',
                    'action': action,
                    'match': match_occurred,
                    'user_profile_image': current_user_profile.main_image.url if current_user_profile.main_image else None,
                    'matched_profile_image': target_profile.main_image.url if match_occurred else None,
                    'matched_profile_name': target_profile.user.first_name if match_occurred else None,
                    'conversation_id': conversation_id,
                }

                return Response(response_data, status=status.HTTP_200_OK if not match_occurred else status.HTTP_201_CREATED)

        except Exception as e:
            # Log the error!
            print(f"Error during swipe action: {e}")  # Replace with proper logging
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


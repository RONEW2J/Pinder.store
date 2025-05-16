from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Match, Conversation, Message, SwipeAction
from apps.profiles.models import Profile
from rest_framework.views import APIView
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer

# Get the User model
User = get_user_model()

class MatchListView(generics.ListAPIView):
    """Lists all matches for the currently authenticated user."""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

class ConversationListView(generics.ListAPIView):
    """Lists all conversations for the currently authenticated user."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.conversations_participated.all().order_by('-updated_at')

class MessageListView(generics.ListAPIView):
    """Lists messages for a specific conversation."""
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
            return Message.objects.filter(conversation=conversation).order_by('created_at')
        return Message.objects.none()

class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().filter(participants=self.request.user)

class UnmatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_unmatch = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = request.user
        u1, u2 = (current_user, user_to_unmatch) if current_user.id < user_to_unmatch.id else (user_to_unmatch, current_user)

        try:
            with transaction.atomic():
                match = get_object_or_404(Match, user1=u1, user2=u2)
                if match.conversation:
                    match.conversation.delete()
                match.delete()
                return Response(
                    {'status': 'success', 'message': 'Successfully unmatched.'},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SwipeActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, profile_id, action):
        if action not in ('like', 'pass'):
            return Response(
                {'error': 'Invalid action'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_profile = Profile.objects.get(pk=profile_id)
            current_user = request.user

            with transaction.atomic():
                # Record swipe action
                SwipeAction.objects.update_or_create(
                    swiper=current_user,
                    profile=target_profile,
                    defaults={'action': action}
                )

                # Check for mutual like
                if action == 'like':
                    mutual_like = SwipeAction.objects.filter(
                        swiper=target_profile.user,
                        profile=current_user.profile,
                        action='like'
                    ).exists()

                    if mutual_like:
                        match, created = Match.objects.get_or_create(
                            user1=current_user,
                            user2=target_profile.user
                        )
                        conversation = Conversation.objects.create()
                        conversation.participants.add(current_user, target_profile.user)
                        
                        return Response({
                            'status': 'match',
                            'match_id': match.id,
                            'conversation_id': conversation.id,
                            'matched_user': {
                                'id': target_profile.user.id,
                                'name': target_profile.user.first_name,
                                'image': target_profile.main_image.url if target_profile.main_image else None
                            }
                        }, status=status.HTTP_201_CREATED)

                return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
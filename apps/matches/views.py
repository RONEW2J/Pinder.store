from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer
from django.shortcuts import render, redirect, get_object_or_404 # Added redirect and get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model # Import get_user_model
from apps.profiles.models import City, Interest


User = get_user_model()

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
        # The permission check for conversation participation is better handled in the list method
        # or by overriding dispatch, to return appropriate HTTP status codes.
        # For get_queryset, we can assume the check will happen.
        conversation_id = self.kwargs.get('conversation_id')
        return Message.objects.filter(conversation_id=conversation_id).order_by('created_at')

    def list(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_id')
        try:
            # Ensure the conversation exists and the user is a participant
            # This will raise Conversation.DoesNotExist if not found or user is not a participant,
            # which DRF handles as a 404 by default if not caught.
            # For more specific 403, we catch it.
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            # Check if the conversation exists at all to differentiate 404 from 403
            if not Conversation.objects.filter(id=conversation_id).exists():
                return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"detail": "You do not have permission to view messages for this conversation."}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset().filter(conversation=conversation) # Filter messages for this specific conversation
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
        return Conversation.objects.filter(participants=self.request.user)

@login_required
def list_matches_view(request): # This view might be for displaying *existing* matches
    user = request.user
    matches_queryset = Match.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).select_related(
        'user1__profile', 
        'user2__profile',
        'conversation'
    ).prefetch_related(
        'user1__profile__photos',
        'user2__profile__photos',
        'conversation__messages' # If you show unread counts or last message
    ).order_by('-created_at')

    # If this view also powers the discovery filters, add city/interest lists
    all_cities_list = City.objects.all().order_by('name')
    all_interests_list = Interest.objects.all().order_by('name')

    context = {
        'all_matches': matches_queryset, # Pass the queryset of Match objects
        'all_cities': all_cities_list,   # For the filter dropdown
        'all_interests': all_interests_list, # For the filter checkboxes
        # 'new_matches': ... # If you have separate logic for this
    }
    return render(request, 'matches.html', context)

@login_required
def chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.all().order_by('created_at')
    other_participant = None
    for participant in conversation.participants.all():
        if participant != request.user:
            other_participant = participant
            break
    other_user_profile = getattr(other_participant, 'profile', None)
    context = {
        'conversation_id': conversation_id,
        'current_user_id': request.user.id,
        'messages': messages,
        'other_user_profile': other_user_profile,
        'conversation_obj': conversation,
    }
    
@login_required
def create_or_get_conversation_view(request, target_user_id):
    target_user = get_object_or_404(User, pk=target_user_id)
    current_user = request.user

    if target_user == current_user:
        # User trying to create a conversation with themselves, redirect or show error
        messages.error(request, "You cannot start a conversation with yourself.")
        return redirect('profiles:profile-display') # Or some other appropriate page

    # Check if a conversation already exists between these two users
    # This query needs to be robust to find the conversation regardless of who is "user1" or "user2"
    # in a hypothetical direct M2M or by checking participants.
    
    # Assuming Conversation.participants is a ManyToManyField to User model
    conversation = Conversation.objects.filter(
        participants=current_user
    ).filter(
        participants=target_user
    ).first() # Get the first one if multiple somehow exist (shouldn't with proper setup)

    if not conversation:
        # No existing conversation, create a new one
        conversation = Conversation.objects.create()
        conversation.participants.add(current_user, target_user)
        # Optionally, create an initial "Match" object if your logic requires it here
        # Or if a Match object is what *leads* to a conversation, this view might be called
        # after a Match is confirmed.
        # For now, we assume clicking "Message" can initiate the conversation.
        
        # Example: If a Match should also be created or confirmed
        # match, created = Match.objects.get_or_create(
        #     user1=min(current_user, target_user, key=lambda u: u.id),
        #     user2=max(current_user, target_user, key=lambda u: u.id),
        #     defaults={'conversation': conversation}
        # )
        # if not created and not match.conversation: # If match existed but no conversation linked
        #     match.conversation = conversation
        #     match.save()

    return redirect('matches:chat-page', conversation_id=conversation.id)

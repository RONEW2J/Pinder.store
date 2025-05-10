from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer
from django.shortcuts import render #
from django.contrib.auth.decorators import login_required

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

@login_required # Ensures only logged-in users can access this page
def list_matches_view(request):
    user = request.user
    # Fetch matches where the current user is either user1 or user2
    matches = Match.objects.filter(Q(user1=user) | Q(user2=user)).select_related('user1', 'user2')

    # Prepare a list of matched profiles to display
    matched_profiles_data = []
    for match in matches:
        other_user = match.user2 if match.user1 == user else match.user1
        # You'd typically fetch the Profile object for other_user here
        # For simplicity, let's assume you have a way to get profile info
        # like profile picture URL and name from the User object or its related Profile.

        # Example: Fetching profile (ensure you have a Profile model linked to User)
        try:
            other_user_profile = other_user.profile # Assumes a OneToOneField 'profile' on User
            profile_pic_url = other_user_profile.photos.filter(is_profile_picture=True).first().image.url if other_user_profile.photos.filter(is_profile_picture=True).exists() else '/static/images/default_avatar.png' # Fallback
        except AttributeError: # If no profile or photos setup
            other_user_profile = None
            profile_pic_url = '/static/images/default_avatar.png'


        matched_profiles_data.append({
            'id': other_user.id, # ID of the matched user
            'username': other_user.username,
            'profile_picture_url': profile_pic_url,
            'conversation_url': f'/chat/{match.id}/' # Assuming match ID can link to a conversation or you use conversation ID
        })

    context = {
        'matched_profiles': matched_profiles_data,
    }
    return render(request, 'matches.html', context)

@login_required
def chat_view(request, conversation_id): # Assuming conversation_id is passed in URL
    # Fetch conversation details, messages, etc.
    # For now, just rendering the template
    # You'd fetch the specific conversation and its messages here
    # and pass them to the context.
    # Also, pass the current user's ID for the JavaScript.
    context = {
        'conversation_id': conversation_id,
        'current_user_id': request.user.id, 
        # 'messages': fetched_messages,
        # 'other_user_profile': other_user_in_chat_profile,
    }
    return render(request, 'chat.html', context)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer
from .forms import MessageForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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

    def _get_conversation(self):
        if not hasattr(self, '_conversation_instance'):
            conversation_id = self.kwargs.get('conversation_id')
            try:
                self._conversation_instance = Conversation.objects.get(
                    id=conversation_id, 
                    participants=self.request.user
                )
            except Conversation.DoesNotExist:
                self._conversation_instance = None
        return self._conversation_instance

    def get_queryset(self):
        conversation = self._get_conversation()
        if conversation:
            return Message.objects.filter(conversation=conversation).order_by('created_at')
        return Message.objects.none()

    def list(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_id')
        if not Conversation.objects.filter(id=conversation_id).exists():
            return Response(
                {"detail": "Conversation not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation = self._get_conversation()
        if not conversation:
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
    

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.profiles.models import City, Interest
from django.contrib import messages
from django.conf import settings
from apps.profiles.models import Profile 

User = get_user_model()

@login_required
def list_matches_view(request):
    user = request.user
    matches_queryset = Match.objects.filter(
        Q(user1=user) | Q(user2=user),
        # is_active=True  # Uncomment if you have this field
    ).select_related(
        'user1__profile',
        'user2__profile',
        'conversation'
    ).prefetch_related(
        'user1__profile__photos',
        'user2__profile__photos',
        'conversation__messages'
    ).order_by('-created_at')

    # Debug: Print raw matches data
    print("All matches:", list(matches_queryset.values_list('user1__username', 'user2__username')))
    print("Other profiles:", [p.user.username for p in Profile.objects.exclude(user=request.user)])

    processed_matches = []
    for match_obj in matches_queryset:
        other_user = match_obj.user2 if match_obj.user1 == user else match_obj.user1
        other_profile = getattr(other_user, 'profile', None)
        
        if settings.DEBUG:
            debug_info = {
                'match_id': match_obj.id,
                'other_user': other_user.username if other_user else None,
                'profile_exists': bool(other_profile),
                'profile_user': other_profile.user.username if (other_profile and hasattr(other_profile, 'user')) else None
            }
            print("DEBUG Match Processing:", debug_info)

        processed_matches.append({
            'match_object': match_obj,
            'other_user_profile': other_profile
        })

    context = {
        'all_matches': processed_matches,
        'all_cities': City.objects.all().order_by('name'),
        'all_interests': Interest.objects.all().order_by('name'),
        'selected_interests': request.GET.getlist('interests'),
    }
    return render(request, 'matches.html', context)

@login_required
def chat_view(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related(
        'participants__profile',
        'messages'
    ).order_by('-updated_at')
    
    return render(request, 'matches/chat_page.html', {
        'conversations': conversations,
        'current_user_id': request.user.id
    })

@login_required
def chat_detail_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=request.user),
        id=conversation_id
    )
    messages = conversation.messages.all().order_by('created_at')
    
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related(
        'participants__profile',
        'messages'
    ).order_by('-updated_at')
    
    return render(request, 'matches/chat_page.html', {
        'active_conversation': conversation,
        'conversations': conversations,
        'messages': messages,
        'current_user_id': request.user.id
    })

@login_required
def send_message_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def create_or_get_conversation_view(request, target_user_id):
    target_user = get_object_or_404(User, pk=target_user_id)
    current_user = request.user

    if target_user == current_user:
        messages.error(request, "You cannot start a conversation with yourself.")
        return redirect('matches:matches-list')

    # Проверяем существующую беседу
    existing_conversation = Conversation.objects.filter(
        participants=current_user
    ).filter(
        participants=target_user
    ).first()

    if existing_conversation:
        return redirect('matches:chat-page', conversation_id=existing_conversation.id)

    # Создаем новую беседу и match
    conversation = Conversation.objects.create()
    conversation.participants.add(current_user, target_user)
    
    # Создаем или обновляем match
    match, created = Match.objects.get_or_create(
        Q(user1=current_user, user2=target_user) | Q(user1=target_user, user2=current_user),
        defaults={'conversation': conversation}
    )
    
    if not created:
        match.conversation = conversation
        match.save()

    return redirect('matches:chat-page', conversation_id=conversation.id)

@login_required
def send_message_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
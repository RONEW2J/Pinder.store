from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, Conversation, Message, SwipeAction
from .serializers import MatchSerializer, ConversationSerializer, MessageSerializer
from .forms import MessageForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
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
    # Get current user's profile
    user_profile = request.user.profile
    
    # Get all matches for the current user
    all_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1__profile', 'user2__profile')

    
    # Prepare match data for template
    matches_data = []
    for match in all_matches:
        other_user = match.user2 if match.user1 == request.user else match.user1
        matches_data.append({
            'match_object': match,
            'other_user_profile': other_user.profile
        })
    
    # Get discovery profiles (excluding matches and blocked users)
    matched_user_ids = [match.user2.id if match.user1 == request.user else match.user1.id 
                       for match in all_matches]
    swiped_profile_ids = SwipeAction.objects.filter(swiper=request.user).values_list('profile_id', flat=True)

    discovery_profiles = Profile.objects.exclude(
        user=request.user
    ).exclude(
        user__id__in=matched_user_ids
    ).exclude(
        id__in=user_profile.blocked_users.values_list('id', flat=True) # Предполагается, что blocked_users это QuerySet профилей
    ).exclude(
        id__in=swiped_profile_ids # Исключаем уже свайпнутые профили
    )
        
    context = {
        'all_matches': matches_data,
        'discovery_profiles': discovery_profiles,  # This is the key fix
        'user': request.user
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
@require_POST # Добавляем декоратор для безопасности, если это API для AJAX
def send_message_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.sender = request.user
        message.save()
        # Для AJAX можно вернуть данные сообщения, если нужно их сразу отобразить на клиенте
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'timestamp': message.created_at.strftime('%Y-%m-%dT%H:%M:%S') # ISO формат
        })
    else:
        # Можно вернуть ошибки формы
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required
def create_or_get_conversation_view(request, target_user_id):
    target_user = get_object_or_404(User, pk=target_user_id) # Добавьте это в начало функции
    current_user = request.user # Добавьте это в начало функции

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
        return redirect('matches:chat-detail', conversation_id=existing_conversation.id)

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

def discover_profiles_view(request):
    # Get current user's profile
    user_profile = request.user.profile
    
    # Get IDs of users you've already matched with
    matched_user_ids = user_profile.matches.values_list('id', flat=True)
    
    # Get IDs of users you've blocked or been blocked by
    blocked_user_ids = user_profile.blocked_users.values_list('id', flat=True)
    
    # Get discovery profiles - exclude yourself, matches, and blocked users
    discovery_profiles = Profile.objects.exclude(
        user=request.user
    ).exclude(
        id__in=matched_user_ids
    ).exclude(
        id__in=blocked_user_ids
    ).exclude(
        # Add any other filters you need (distance, preferences, etc.)
    )
    
    return render(request, 'matches.html', {
        'discovery_profiles': discovery_profiles,
        # other context data...
    })

@login_required
@require_POST
def swipe_action_view(request, profile_id, action):
    current_user_profile = request.user.profile
    target_profile = Profile.objects.get(id=profile_id)

    if current_user_profile == target_profile:
        return JsonResponse({'status': 'error', 'message': 'Cannot swipe your own profile'}, status=400)

    # Записываем действие
    SwipeAction.objects.update_or_create(
        swiper=request.user, # или swiper_profile=current_user_profile
        profile=target_profile,
        defaults={'action': action}
    )

    match_occurred = False
    if action == 'like':
        if SwipeAction.objects.filter(swiper=target_profile.user, profile=current_user_profile, action='like').exists():
            match_occurred = True
            # Используем метод модели для создания мэтча и беседы
            match, conversation = Match.create_match_and_conversation(request.user, target_profile.user)

            # Добавляем ID беседы в ответ, если клиент его использует
            response_data = {
                'status': 'success',
                'action': action,
                'match': match_occurred,
                'user_profile_image': current_user_profile.main_image.url if current_user_profile.main_image else None,
                'matched_profile_image': target_profile.main_image.url if target_profile.main_image else None,
                'matched_profile_name': target_profile.user.first_name,
                'conversation_id': conversation.id # ID для возможного редиректа в чат
            }
            return JsonResponse(response_data)

    # Если не 'like' или не мэтч
    return JsonResponse({
        'status': 'success',
        'action': action,
        'match': match_occurred,
        # ... (остальные поля, если нужны, но без conversation_id, если мэтча не было)
    })
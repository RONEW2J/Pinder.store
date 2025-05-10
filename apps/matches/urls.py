from django.urls import path
from . import views 


app_name = 'matches'

urlpatterns = [
    # API Endpoints
    path('api/my-matches/', views.MatchListView.as_view(), name='api-my-matches-list'),
    path('api/conversations/', views.ConversationListView.as_view(), name='api-conversation-list'),
    path('api/conversations/<int:id>/', views.ConversationDetailView.as_view(), name='api-conversation-detail'),
    path('api/conversations/<int:conversation_id>/messages/', views.MessageListView.as_view(), name='api-message-list'),

    # UI (HTML Template) Endpoints
    # Assuming list_matches_view is your main page for discovery/matches list
    path('', views.list_matches_view, name='matches-list-discover'), # More descriptive name
    path('chat/<int:conversation_id>/', views.chat_view, name='chat-page'),
    # You'll need to create this view and URL pattern:
    path('create-conversation/<int:target_user_id>/', views.create_or_get_conversation_view, name='create-conversation'),
]
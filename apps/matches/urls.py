from django.urls import path
from . import views  # For function-based views like list_matches_view, chat_view
from . import views_api # For DRF views like MatchListView, ConversationListView


app_name = 'matches'

urlpatterns = [
    # API Endpoints
    path('api/my-matches/', views_api.MatchListView.as_view(), name='api-my-matches-list'),
    path('api/conversations/', views_api.ConversationListView.as_view(), name='api-conversation-list'),
    path('api/conversations/<int:id>/', views_api.ConversationDetailView.as_view(), name='api-conversation-detail'),
    path('api/conversations/<int:conversation_id>/messages/', views_api.MessageListView.as_view(), name='api-message-list'),

    # UI (HTML Template) Endpoints
    # Assuming list_matches_view is your main page for discovery/matches list
    path('', views.list_matches_view, name='matches-list-discover'), # More descriptive name
    path('chat/<int:conversation_id>/', views.chat_view, name='chat-page'),
    # You'll need to create this view and URL pattern:
    path('conversations/create/<int:target_user_id>/', 
         views.create_or_get_conversation_view, 
         name='create_conversation'),
]
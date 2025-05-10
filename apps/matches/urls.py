from django.urls import path
from . import views as template_views 
from . import views_api 

app_name = 'matches'

urlpatterns = [
    # API Endpoints
    path('api/my-matches/', views_api.MatchListView.as_view(), name='api-my-matches-list'),
    path('api/conversations/', views_api.ConversationListView.as_view(), name='api-conversation-list'),
    path('api/conversations/<int:id>/', views_api.ConversationDetailView.as_view(), name='api-conversation-detail'), # For retrieving a specific conversation
    path('api/conversations/<int:conversation_id>/messages/', views_api.MessageListView.as_view(), name='api-message-list'),

    # UI (HTML Template) Endpoints
    path('', template_views.list_matches_view, name='matches-page'),
    path('chat/<int:conversation_id>/', template_views.chat_view, name='chat-page'),
]

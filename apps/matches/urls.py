from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('my-matches/', views.MatchListView.as_view(), name='my-matches-list'),
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    # If you need a detail view for a conversation (e.g., for the signal's reverse lookup if it's backend)
    path('conversations/<int:id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
]
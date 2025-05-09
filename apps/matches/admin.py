from django.contrib import admin
from .models import Match, Conversation, Message

# Register your models here.

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('participants',) # Makes ManyToManyField easier to manage

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at', 'sender')
    search_fields = ('content', 'sender__username', 'conversation__id')

    def content_preview(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

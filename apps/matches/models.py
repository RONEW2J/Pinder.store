from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

class Match(models.Model):
    """Represents a mutual like between two users."""
    # user1 is conventionally the user with the lower ID to ensure uniqueness of the pair
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Match')
        verbose_name_plural = _('Matches')
        unique_together = ('user1', 'user2') # Ensures a pair can only match once
        constraints = [
            models.CheckConstraint(
                check=Q(user1_id__lt=models.F('user2_id')),
                name='user1_id_lt_user2_id_match'
            )
        ]

    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"

    @classmethod
    def create_match_and_conversation(cls, user_a, user_b):
        """
        Creates a Match instance and its associated Conversation.
        Ensures user1.id < user2.id for the Match.
        Returns (match, conversation).
        """
        u1, u2 = (user_a, user_b) if user_a.id < user_b.id else (user_b, user_a)
        
        match, match_created = cls.objects.get_or_create(user1=u1, user2=u2)
        
        # Get or create the conversation for these two users
        conversation, conv_created = Conversation.get_or_create_for_users(u1, u2)
        
        return match, conversation

class Conversation(models.Model):
    """A conversation between two users, typically after a match."""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations_participated')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        # Note: Uniqueness for a pair with ManyToManyField is typically handled at the application level
        # via methods like get_or_create_for_users.

    def __str__(self):
        p_list = list(self.participants.all().order_by('username')) # Consistent ordering
        if len(p_list) == 2:
            return f"Conversation between {p_list[0].username} and {p_list[1].username} (ID: {self.id})"
        return f"Conversation (ID: {self.id}, Participants: {len(p_list)})"

    @classmethod
    def get_or_create_for_users(cls, user_a, user_b):
        """
        Retrieves or creates a unique conversation for a pair of users.
        Returns (conversation, created_boolean).
        """
        # Query for conversations involving both users and having exactly two participants
        conversation = cls.objects.annotate(
            num_participants=Count('participants')
        ).filter(
            participants=user_a
        ).filter(
            participants=user_b
        ).filter(
            num_participants=2
        ).first()

        if conversation:
            return conversation, False
        else:
            conversation = cls.objects.create()
            conversation.participants.add(user_a, user_b)
            return conversation, True

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages_in_conversation')
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in conversation {self.conversation.id}"

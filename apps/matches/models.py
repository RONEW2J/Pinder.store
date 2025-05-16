from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user2', on_delete=models.CASCADE)
    conversation = models.OneToOneField('Conversation', on_delete=models.SET_NULL, null=True, blank=True, related_name='match_record') # Added related_name for clarity
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')
        # The check constraint is likely defined in a migration, but this is where you'd add model-level constraints
        # constraints = [
        #     models.CheckConstraint(check=models.Q(user1_id__lt=models.F('user2_id')), name='user1_id_lt_user2_id_match_model')
        # ]
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"

    def save(self, *args, **kwargs):
        # Ensure user1.id is always less than user2.id
        if self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    @classmethod
    def create_match_and_conversation(cls, user_a, user_b):
        u1, u2 = (user_a, user_b) if user_a.id < user_b.id else (user_b, user_a)

        # Получаем или создаем беседу
        conversation, conv_created = Conversation.get_or_create_for_users(u1, u2)

        # Получаем или создаем мэтч, связывая его с беседой
        match, match_created = cls.objects.get_or_create(
            user1=u1, user2=u2,
            defaults={'conversation': conversation} # Связываем при создании
        )

        # Если мэтч уже существовал, но не был связан с беседой (маловероятно при такой логике, но для надежности)
        if not match_created and not match.conversation:
            match.conversation = conversation
            match.save(update_fields=['conversation'])

        return match, conversation

class Conversation(models.Model):
    """A conversation between two users, typically after a match."""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations_participated')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    other_profile = models.ForeignKey(
        'profiles.Profile', 
        on_delete=models.CASCADE,
        related_name='conversations'
    )

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
    
class SwipeAction(models.Model):
    swiper = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_given', on_delete=models.CASCADE)
    profile = models.ForeignKey('profiles.Profile', related_name='swipes_received', on_delete=models.CASCADE)
    action = models.CharField(max_length=4, choices=[('like', 'Like'), ('pass', 'Pass')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'profile')

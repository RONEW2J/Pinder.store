from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(_('Notification Type'), max_length=50) # e.g., 'new_message', 'new_match'
    title = models.CharField(_('Title'), max_length=255)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(_('Is Read'), default=False)
    link = models.URLField(_('Link'), blank=True, null=True) # Optional link to navigate to
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

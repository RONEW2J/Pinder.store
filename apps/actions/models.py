from django.db import models
from django.conf import settings 

# Create your models here.
class Swipe(models.Model):
    swiper = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_made', on_delete=models.CASCADE)  # Кто свайпнул
    swiped_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_received', on_delete=models.CASCADE)  # Кого свайпнули
    action = models.CharField(max_length=4, choices=[('LIKE', 'Like'), ('PASS', 'Pass')]) # max_length should fit 'LIKE' or 'PASS'
    timestamp = models.DateTimeField(auto_now_add=True)
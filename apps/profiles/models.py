from django.db import models
from django.conf import settings # Use settings.AUTH_USER_MODEL
from django.contrib.gis.db.models import PointField # Import PointField from GeoDjango
# Alternatively, you can use:
# from django.contrib.auth import get_user_model
# User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )  # Расширение данных пользователя
    age = models.PositiveIntegerField(null=True, blank=True) # Consider if age can be optional initially
    location = PointField(null=True, blank=True)  # GeoDjango - ensure PostGIS setup if using this
    interests = models.ManyToManyField('Interest', blank=True)

class Interest(models.Model): # You'll need to define the Interest model
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Swipe(models.Model):
    swiper = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_made', on_delete=models.CASCADE)  # Кто свайпнул
    swiped_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_received', on_delete=models.CASCADE)  # Кого свайпнули
    action = models.CharField(max_length=4, choices=[('LIKE', 'Like'), ('PASS', 'Pass')]) # max_length should fit 'LIKE' or 'PASS'
    timestamp = models.DateTimeField(auto_now_add=True)
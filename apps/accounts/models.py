from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('OTHER', 'Other'),
    ], blank=True)
    
    def __str__(self):
        return self.username
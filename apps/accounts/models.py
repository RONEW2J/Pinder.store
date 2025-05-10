from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('OTHER', 'Other'),
    ]
    INTERESTED_IN_CHOICES = [
        ('MEN', 'Men'),
        ('WOMEN', 'Women'),
        ('EVERYONE', 'Everyone'),
    ]
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    interested_in = models.CharField(max_length=10, choices=INTERESTED_IN_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.username
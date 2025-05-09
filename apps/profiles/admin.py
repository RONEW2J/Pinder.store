from django.contrib import admin
from .models import Profile, Interest, Photo # Added Photo

# Register your models here.
admin.site.register(Profile)
admin.site.register(Interest)
admin.site.register(Photo) # Register the new Photo model

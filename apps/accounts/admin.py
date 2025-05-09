from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
# For a custom user model, you might want to customize the admin display
admin.site.register(User, UserAdmin)

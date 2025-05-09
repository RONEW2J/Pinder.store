from django.contrib import admin
from .models import Swipe

# Register your models here.
@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'swiper', 'swiped_user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('swiper__username', 'swiped_user__username')

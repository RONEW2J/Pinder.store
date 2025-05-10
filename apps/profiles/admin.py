from django.contrib import admin
from .models import Profile, Interest, Photo, City # Added Photo

# Register models that don't have a custom ModelAdmin class with a decorator
admin.site.register(Photo)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'age', 'gender') # Add city here
    search_fields = ('user__username', 'user__email', 'city__name') # Search by city name
    list_filter = ('city', 'gender', 'interests')
    raw_id_fields = ('user', 'city') # Good for ForeignKey fields with many options
    # Remove any GeoAdmin specific configurations
from django.urls import path
from .views import (UserProfileDetailView, InterestListCreateView, ProfileListView,
                    user_profile_display_view, profile_edit_view, photo_upload_view) # Import photo_upload_view


app_name = 'profiles'

urlpatterns = [
     # UI View for displaying profile
    path('me/view/', user_profile_display_view, name='profile-display'), # Example URL
    path('me/edit/', profile_edit_view, name='profile-edit'), # URL for editing profile
    path('me/photos/upload/', photo_upload_view, name='photo-upload'), # URL for uploading photos
    # API Endpoints
    path('api/me/', UserProfileDetailView.as_view(), name='user-profile-detail-api'), # API for profile data

]
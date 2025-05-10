from django.urls import path
from .views import (UserProfileDetailView, InterestListCreateView, ProfileListView,
                    user_profile_display_view, profile_edit_view) # Import profile_edit_view


app_name = 'profiles'

urlpatterns = [
     # UI View for displaying profile
    path('me/view/', user_profile_display_view, name='profile-display'), # Example URL
    path('me/edit/', profile_edit_view, name='profile-edit'), # URL for editing profile

    # API Endpoints
    path('api/me/', UserProfileDetailView.as_view(), name='user-profile-detail-api'), # API for profile data

]
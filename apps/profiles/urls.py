# c:\Users\user\PycharmProjects\TinderCloneProject\apps\profiles\urls.py
from django.urls import path, include
# from rest_framework.routers import DefaultRouter # Not using router for now with generic views
from .views import (
    # These are your existing generic class-based views
    UserProfileDetailView, InterestListCreateView, ProfileListView,
    PhotoListCreateView, PhotoDetailView,
    # Your existing function-based views for UI
    user_profile_display_view, profile_edit_view, photo_upload_view, photo_delete_view
)

app_name = 'profiles'

# Router setup is removed as we are not using ViewSets in this immediate fix.
# If you refactor views to ViewSets later, you can reintroduce the router.
# router = DefaultRouter()
# router.register(r'me', UserProfileViewSet, basename='profile-me')
# router.register(r'profiles', ProfileViewSet, basename='profile')
# router.register(r'interests', InterestViewSet, basename='interest')
# router.register(r'photos', PhotoViewSet, basename='photo')


urlpatterns = [
    # UI Views
    path('me/view/', user_profile_display_view, name='profile-display'),
    path('me/edit/', profile_edit_view, name='profile-edit'),
    path('me/photos/upload/', photo_upload_view, name='photo-upload'),
    path('me/photos/<int:photo_id>/delete/', photo_delete_view, name='photo-delete'),

    # API URLs for DRF (defined manually for generic views)
    path('api/me/', UserProfileDetailView.as_view(), name='api-profile-me'),
    path('api/interests/', InterestListCreateView.as_view(), name='api-interest-list-create'),
    path('api/profiles/', ProfileListView.as_view(), name='api-profile-list'),
    path('api/photos/', PhotoListCreateView.as_view(), name='api-photo-list-create'),
    path('api/photos/<int:pk>/', PhotoDetailView.as_view(), name='api-photo-detail'),
    # path('api/', include(router.urls)), # This line is removed
]

from django.urls import path
from .views import (UserProfileDetailView, InterestListCreateView, ProfileListView)
 # PhotoListCreateView, PhotoDetailView # You'll create these views

app_name = 'profiles'

urlpatterns = [
    path('me/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('interests/', InterestListCreateView.as_view(), name='interest-list-create'),
    path('', ProfileListView.as_view(), name='profile-list'), 
    # path('me/photos/', PhotoListCreateView.as_view(), name='photo-list-create'),
    # path('me/photos/<int:pk>/', PhotoDetailView.as_view(), name='photo-detail'),
]
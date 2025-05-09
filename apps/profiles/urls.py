from django.urls import path
from .views import UserProfileDetailView, InterestListCreateView

app_name = 'profiles'

urlpatterns = [
    path('me/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('interests/', InterestListCreateView.as_view(), name='interest-list-create'),
]
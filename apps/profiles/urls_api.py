# c:\Users\user\PycharmProjects\TinderCloneProject\apps\profiles\urls_api.py
from django.urls import path
from .views import ( # Import directly from the views.py file in the current app (profiles)
    UserProfileDetailView,
    InterestListCreateView,
    ProfileListView,
    PhotoListCreateView,
    PhotoDetailView
)

app_name = 'profiles_api' # Define app_name for namespacing

urlpatterns = [
    path('me/', UserProfileDetailView.as_view(), name='me'), # e.g., /api/v1/profiles/me/
    path('interests/', InterestListCreateView.as_view(), name='interests-list-create'),
    path('all/', ProfileListView.as_view(), name='list'), # e.g., /api/v1/profiles/all/
    path('photos/', PhotoListCreateView.as_view(), name='photos-list-create'),
    path('photos/<int:pk>/', PhotoDetailView.as_view(), name='photos-detail'),
]

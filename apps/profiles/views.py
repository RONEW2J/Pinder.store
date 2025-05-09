from django.shortcuts import render
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend # Import DjangoFilterBackend

from .models import Profile, Interest
from .serializers import ProfileSerializer, InterestSerializer


# Create your views here.

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the profile of the currently authenticated user.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure a profile exists for the user, or create one if using signals isn't enough
        # (though signals should handle this)
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class InterestListCreateView(generics.ListCreateAPIView):
    """
    List all interests or create a new one.
    """
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anyone to see, only auth to create

class ProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'interests']
    search_fields = ['user__username', 'bio']
    
    def get_queryset(self):
        return Profile.objects.exclude(user=self.request.user)

    # If you had this line before, it was correct to keep it in get_queryset
    # def get_queryset(self):
    #     return Profile.objects.exclude(user=self.request.user).prefetch_related('interests', 'photos')
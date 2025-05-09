from django.shortcuts import render
from rest_framework import generics, permissions
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

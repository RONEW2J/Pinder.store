from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend # Import DjangoFilterBackend
from django.db.models import Q, Case, When, F, IntegerField
from django.contrib import messages

from .models import Profile, Interest, Photo # Added Photo
from apps.actions.models import Swipe # For filtering based on swipes
from apps.matches.models import Match # For filtering based on matches
from .serializers import ProfileSerializer, InterestSerializer, PhotoSerializer # Added PhotoSerializer
from .forms import ProfileEditForm 

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D # Distance object
from django.contrib.gis.db.models.functions import Distance as DistanceFunc

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

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
    # Assuming 'interests' can be filtered by ID or name (e.g., interests__name=Music)
    # 'gender' and 'bio' were removed as they are not on the current Profile model.
    # Add them to the model if you intend to filter/search by them.
    filterset_fields = ['interests', 'age'] # Example: ?age=25 or ?interests=1 (by ID)
    search_fields = ['user__username', 'interests__name'] # Search by username or interest names
    ordering_fields = ['age', 'user__date_joined', 'distance'] # Allow ordering by these, 'distance' if annotated
    
    def get_queryset(self):
        user = self.request.user
        queryset = Profile.objects.select_related('user').prefetch_related('interests', 'photos').exclude(user=user)

        # 1. Filter out users the current user has already swiped "PASS" on.
        passed_user_ids = Swipe.objects.filter(
            swiper=user,
            action='PASS'
        ).values_list('swiped_user_id', flat=True)
        queryset = queryset.exclude(user_id__in=passed_user_ids)

        # 2. Filter out users the current user has already matched with.
        matches_as_user1 = Match.objects.filter(user1=user).values_list('user2_id', flat=True)
        matches_as_user2 = Match.objects.filter(user2=user).values_list('user1_id', flat=True)
        all_matched_user_ids = set(list(matches_as_user1) + list(matches_as_user2))
        queryset = queryset.exclude(user_id__in=all_matched_user_ids)

        # 3. Potentially, filter by proximity (GeoDjango)
        # This requires the current user to have a location set in their profile.
        try:
            user_profile = user.profile
            if user_profile.location:
                user_location = user_profile.location # This is a Point object
                
                # Get search radius from query params, e.g., ?radius_km=50
                # Default to a reasonable value if not provided.
                search_radius_km_str = self.request.query_params.get('radius_km', '50')
                try:
                    search_radius_km = float(search_radius_km_str)
                except ValueError:
                    search_radius_km = 50 # Default if invalid param

                # Annotate with distance and filter
                # Note: For dwithin to work efficiently, your location field should have a spatial index.
                queryset = queryset.annotate(
                    distance=DistanceFunc('location', user_location)
                ).filter(
                    location__isnull=False, # Only consider profiles with a location
                    distance__lte=D(km=search_radius_km)
                )
                # If ordering by distance is desired by default when radius is applied:
                # queryset = queryset.order_by('distance') 
                # However, DRF's OrderingFilter will handle ?ordering=distance if 'distance' is in ordering_fields
        except Profile.DoesNotExist:
            # User has no profile, so location-based filtering cannot be applied from their perspective.
            # Depending on desired behavior, you might return an empty queryset or just skip this filter.
            pass # Skipping distance filter if user has no profile or location
        except AttributeError: # If user.profile.location is None
            pass

        return queryset

# You'll need to create these views for photo management
class PhotoListCreateView(generics.ListCreateAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Photo.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

class PhotoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Photo.objects.filter(profile__user=self.request.user)
    
@login_required
def user_profile_display_view(request):
    # Assuming a Profile is created for each User, e.g., via a signal
    # If not, you might need get_or_create
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Handle case where profile doesn't exist, maybe create it
        # or redirect to a profile creation page.
        # For now, let's assume it should exist.
        # If you have a signal to create Profile on User creation, this should be fine.
        # If not, you might want to redirect to a "create profile" page.
        return render(request, 'profiles/profile_not_found.html') # Or some other handling

    context = {'profile': profile}
    return render(request, 'profiles/profile_display.html', context)

@login_required
def profile_edit_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Handle case where profile doesn't exist, perhaps create one
        # For now, redirecting or showing an error.
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('profiles:profile-display') # Or 'home'

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profiles:profile-display')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'profiles/profile_edit_form.html', {'form': form, 'profile': profile})
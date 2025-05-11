from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend # Import DjangoFilterBackend
from django.db.models import Q, Case, When, F, IntegerField
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Profile, Interest, Photo # Added Photo
from apps.actions.models import Swipe # For filtering based on swipes
from apps.matches.models import Match # For filtering based on matches
from .serializers import ProfileSerializer, InterestSerializer, PhotoSerializer # Added PhotoSerializer
from .forms import ProfileEditForm, PhotoUploadForm

# GeoDjango imports are no longer needed for profile editing if using city
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.http import require_POST

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

@method_decorator(cache_page(60, key_prefix='profile_list'), name='list')
class ProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['interests', 'age'] 
    search_fields = ['user__username', 'interests__name'] 
    ordering_fields = ['age', 'user__date_joined', 'distance'] 
    
    def get_queryset(self):
        user = self.request.user
        queryset = Profile.objects.select_related('user').prefetch_related('interests', 'photos').exclude(user=user)
        
        # --- DEBUG PRINT START ---
        print(f"User {user.username} - Initial discoverable profiles count: {queryset.count()}")
        # --- DEBUG PRINT END ---

        # 1. Filter out users the current user has already swiped "PASS" on.
        passed_user_ids = Swipe.objects.filter(
            swiper=user,
            action='PASS'
        ).values_list('swiped_user_id', flat=True)
        queryset = queryset.exclude(user_id__in=passed_user_ids)

        # --- DEBUG PRINT START ---
        print(f"User {user.username} - After PASS filter count: {queryset.count()}")
        # --- DEBUG PRINT END ---

        # 2. Filter out users the current user has already matched with.
        matches_as_user1 = Match.objects.filter(user1=user).values_list('user2_id', flat=True)
        matches_as_user2 = Match.objects.filter(user2=user).values_list('user1_id', flat=True)
        all_matched_user_ids = set(list(matches_as_user1) + list(matches_as_user2))
        queryset = queryset.exclude(user_id__in=all_matched_user_ids)

        # --- DEBUG PRINT START ---
        print(f"User {user.username} - After MATCH filter count: {queryset.count()}")
        # --- DEBUG PRINT END ---

        # 3. Filter by city and interests (if provided in query params)
        city_id = self.request.query_params.get('city')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        
        # --- DEBUG PRINT START ---
        # Added this print statement to see the count after city filtering
        print(f"User {user.username} - After CITY filter (city_id: {city_id}) count: {queryset.count()}")
        # --- DEBUG PRINT END ---

        interest_ids = self.request.query_params.getlist('interests') 
        if interest_ids:
            queryset = queryset.filter(interests__id__in=interest_ids).distinct()

        # --- DEBUG PRINT START ---
        # Added this print statement to see the count after interest filtering
        print(f"User {user.username} - After INTERESTS filter (ids: {interest_ids}) count: {queryset.count()}")
        # --- DEBUG PRINT END ---
        
        # --- DEBUG PRINT START ---
        # This was the final print statement suggested
        print(f"User {user.username} - Final discoverable profiles count: {queryset.count()}")
        # --- DEBUG PRINT END ---
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
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('profiles:profile-display')

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        print(f"Form submitted. POST data: {request.POST}")
        if form.is_valid():
            print(f"Form is valid. Cleaned data: {form.cleaned_data}")
            
            # The form now handles the 'city' field directly.
            # No need for manual latitude/longitude or Point object creation here.
            updated_profile = form.save() # commit=True is default, this will save the instance and M2M data if form is configured correctly.
                                          # If you had commit=False, you'd need form.save_m2m() later.

            # If ProfileEditForm is a ModelForm and 'interests' is a ManyToManyField,
            # and it's included in form.Meta.fields, form.save() handles it.
            # If you used commit=False above, you would need:
            # updated_profile.save() # first save the instance
            # form.save_m2m()      # then save M2M data
            
            # Critical Debugging Step: Re-fetch from DB and check bio
            fresh_profile_check = Profile.objects.get(pk=updated_profile.pk)
            print(f"Bio from DB immediately after save: {fresh_profile_check.bio}")
            
            # Debug print to verify save
            print(f"Updated profile bio: {updated_profile.bio}, city: {updated_profile.city}")
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profiles:profile-display')
        else:
            print(f"Form is invalid. Errors: {form.errors}") # For debugging if form validation fails
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'profiles/profile_edit_form.html', {'form': form, 'profile': profile})

@login_required
def photo_upload_view(request):
    profile = request.user.profile # Assuming profile exists
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.profile = profile

            # If this photo is marked as the avatar, unmark any other avatars for this profile
            if photo.is_profile_avatar: # This is True if the checkbox was checked
                Photo.objects.filter(profile=profile, is_profile_avatar=True).update(is_profile_avatar=False)
            photo.save()
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('profiles:profile-display') # Redirect to view profile
    else:
        form = PhotoUploadForm()
    return render(request, 'profiles/photo_upload_form.html', {'form': form})

@login_required
@require_POST # Ensure this view only accepts POST requests for deletion
def photo_delete_view(request, photo_id):
    try:
        photo = get_object_or_404(Photo, pk=photo_id)
    except Photo.DoesNotExist:
         # This case is actually handled by get_object_or_404, but good for clarity
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # AJAX
            return JsonResponse({'status': 'error', 'message': 'Photo not found.'}, status=404)
        messages.error(request, 'Photo not found.')
        return redirect('profiles:profile-display') # Or wherever appropriate

    # Security check: Ensure the logged-in user owns the profile to which this photo belongs
    if photo.profile.user != request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # AJAX
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this photo.'}, status=403)
        messages.error(request, 'You do not have permission to delete this photo.')
        return redirect('profiles:profile-display') # Or wherever appropriate

    # If this was the avatar, and you want to clear the avatar status, you could do it here.
    # However, the `main_image` property will now handle finding a new avatar or returning None.
    # If you wanted to explicitly pick a new avatar, that's more complex UI.
    
    photo_was_avatar = photo.is_profile_avatar
    photo.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # AJAX
        response_data = {'status': 'success', 'message': 'Photo deleted successfully.'}
        if photo_was_avatar:
            # Optionally, tell the client the avatar might have changed so it can refresh the main image
            response_data['avatar_changed'] = True 
            # You might also want to send back the URL of the new main_image if one is auto-selected by the property
            new_main_image = request.user.profile.main_image
            response_data['new_avatar_url'] = new_main_image.url if new_main_image else None
        return JsonResponse(response_data)
    
    messages.success(request, 'Photo deleted successfully!')
    return redirect('profiles:profile-display')

@login_required
def view_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    return render(request, 'profiles/view_profile.html', {'profile': profile})
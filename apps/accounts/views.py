from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm # UserCreationForm removed from here
from .forms import CustomUserCreationForm # Import your custom form

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    # If you don't plan to customize the token (e.g., by adding custom claims via a serializer),
    # you can remove this class and use TokenObtainPairView directly in your urls.py.
    pass

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not request.POST.get('remember_me', None):
                    request.session.set_expiry(0) # Session expires when browser closes
                # else: use default session expiry (from settings.SESSION_COOKIE_AGE)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home') # Or to a profile page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

def register_view(request): # Corrected: This should be a standalone function
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # The Profile instance is automatically created by a signal (see apps.profiles.signals.py).
            # Fields like 'birth_date', 'gender', 'interested_in' are on the User model itself
            # and are handled by form.save() because CustomUserCreationForm is based on the User model.

            # If you've added fields to CustomUserCreationForm that belong to the Profile model (e.g., 'age'),
            # you can update the user's profile here.
            age_data = form.cleaned_data.get('age')
            # Ensure profile exists before trying to access it. The signal should create it.
            # A more robust check might be to try/except Profile.DoesNotExist if the signal could fail or be delayed.
            profile_exists = hasattr(user, 'profile') 
            if age_data is not None and profile_exists: 
                user.profile.age = age_data
                user.profile.save()
            # Specify the backend when logging in, as multiple are configured
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home') # Or to a profile setup page
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')
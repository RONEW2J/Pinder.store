from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Optionally log the user in directly
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home') # Or to a profile setup page
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'account/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views # Import Django's built-in auth views
from .views import (
    RegisterView as ApiRegisterView,  # API Register View
    CustomTokenObtainPairView,        # API Custom Token View (if needed, else use default)
    ProfileView,                      # API Profile View
    login_view,                       # Page login view
    register_view as page_register_view, # Page register view
    logout_view,                      # Page logout view
)

app_name = 'accounts'

urlpatterns = [
    # API Endpoints (prefixed with 'api/' within this app's URLs)
    path('api/register/', ApiRegisterView.as_view(), name='api_register'),
    path('api/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/profile/', ProfileView.as_view(), name='api_profile'), # Added API profile URL

    # Page (HTML Form) Endpoints
    path('login/', login_view, name='login_page'),
    path('register/', page_register_view, name='register_page'),
    path('logout/', logout_view, name='logout_page'),

    # Password Reset URLs (using Django's built-in views)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
]
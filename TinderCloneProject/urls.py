"""
URL configuration for TinderCloneProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin # type: ignore
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Unchanged lines # <--- THIS IS LIKELY THE ISSUE
# For Swagger (drf-yasg)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import home_view, terms_view, privacy_view # Import terms_view and privacy_view
from django.views.generic import RedirectView # Import RedirectView


schema_view = get_schema_view(
   openapi.Info( # <--- Line 21 is likely here or just after the problematic "Unchanged lines"
      title="TinderClone API",
      default_version='v1',
      description="API documentation for the TinderClone Project",
      terms_of_service="https://www.google.com/policies/terms/", # Replace
      contact=openapi.Contact(email="contact@tinderclone.local"), # Replace
      license=openapi.License(name="BSD License"), # Replace
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path('', RedirectView.as_view(url='/swagger/', permanent=False)), # Add this line to redirect root to Swagger
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('accounts/', include('allauth.urls')), 
    path('social-auth/', include('social_django.urls', namespace='social')), # For python-social-auth
    path('profiles/', include('apps.profiles.urls', namespace='profiles')), # For your custom profile UI and API
    path('api/matches/', include('apps.matches.urls', namespace='matches_ui')),
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/actions/', include('apps.actions.urls')),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    # Silk profiler
    if 'silk' in settings.INSTALLED_APPS:
        urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files during development (if not handled by runserver automatically)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

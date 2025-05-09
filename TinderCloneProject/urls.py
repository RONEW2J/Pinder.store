from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static

# For Swagger (drf-yasg)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
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
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/profiles/', include('apps.profiles.urls')),
    path('api/matches/', include('apps.matches.urls')), # Assuming you'll create this
    # path('api/notifications/', include('apps.notifications.urls')), # Assuming

    # Swagger UI
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    # Silk profiler
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files during development (if not handled by runserver automatically)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


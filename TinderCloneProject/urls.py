from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import home_view, terms_view, privacy_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),

    # Ваши приложения
    path('accounts/', include('allauth.urls')),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('profiles/', include('apps.profiles.urls', namespace='profiles')),
    path('api/v1/profiles/', include('apps.profiles.urls_api', namespace='profiles_api')),
    path('api/matches/', include('apps.matches.urls', namespace='matches')),

    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),

    # drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    if 'silk' in settings.INSTALLED_APPS:
        urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

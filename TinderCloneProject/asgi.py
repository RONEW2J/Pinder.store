import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.matches.routing # Or wherever your top-level routing for websockets is

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TinderCloneProject.settings')

# Get the default Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.matches.routing.websocket_urlpatterns # Point to your app's routing
        )
    ),
})

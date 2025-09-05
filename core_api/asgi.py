import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# ✅ import community routing properly
import community.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_api.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            community.routing.websocket_urlpatterns
        )
    ),
})

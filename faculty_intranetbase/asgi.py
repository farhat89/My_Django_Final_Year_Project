"""
ASGI config for faculty_intranetbase project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from authentication.middleware import WebSocketAuthMiddleware
from authentication import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faculty_intranetbase.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": WebSocketAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})

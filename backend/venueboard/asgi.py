"""
ASGI config for venueboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venueboard.settings')
django.setup()

from django.conf import settings
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from realtime.routing import websocket_urlpatterns
from realtime.middleware import JWTAuthMiddleware


application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(get_asgi_application()) if settings.DEBUG else get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})

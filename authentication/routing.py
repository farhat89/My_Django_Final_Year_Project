# authentication/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/collaboration/(?P<collab_uuid>[0-9a-f-]+)/$', consumers.CollaborationConsumer.as_asgi()),
]
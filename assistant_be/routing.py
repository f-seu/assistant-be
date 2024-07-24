# myapp/routing.py

from django.urls import path
from recommend.consumers import Consumer
websocket_urlpatterns = [
    path('ws/recommand/', Consumer.as_asgi()),
]

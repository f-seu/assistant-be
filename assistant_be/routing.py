from django.urls import path
from recommend.consumers import Consumer

websocket_urlpatterns = [
    path('ws/recommend', Consumer.as_asgi()),
]

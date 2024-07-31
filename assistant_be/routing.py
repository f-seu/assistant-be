from django.urls import path
from recommend.consumers import Consumer
from chat.messsage_consumer import MessageConsumer
websocket_urlpatterns = [
    path('ws/recommend', Consumer.as_asgi()),
    path('ws/chat', MessageConsumer.as_asgi()),
]

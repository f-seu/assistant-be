"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""


from django.urls import path
from recommend.consumers import Consumer
websocket_urlpatterns = [
    path('ws/recommand/', Consumer.as_asgi()),
]

"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

"""
URL configuration for assistant_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chat.views import ChatView,MessageView,ChatNumView,ChatListView
from mycalendar.views import CalendarView,PlanView,HasCalendarView
from recommend.views import RecommendView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', ChatView.as_view()),
    path('api/chat-list/', ChatListView.as_view()),
    path('api/chat-message/', MessageView.as_view()),
    path('api/chat-num/', ChatNumView.as_view()),

    path('api/calendar/', CalendarView.as_view()),
    path('api/has-calendar/', HasCalendarView.as_view()),

    path('api/plan/', PlanView.as_view()),
    path('api/recommend',RecommendView.as_view()),
    path('api-auth/', include('rest_framework.urls')),
]

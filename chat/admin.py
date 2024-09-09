"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.contrib import admin
from .models import ChatModel,MessageModel


@admin.register(ChatModel)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_at')
    search_fields = ('name',)

@admin.register(MessageModel)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'role', 'timestamp', 'content')
    search_fields = ('role', 'content')
    list_filter = ('timestamp',)

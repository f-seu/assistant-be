"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from rest_framework import serializers
from .models import ChatModel, MessageModel


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'chat', 'role', 'content', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    message_num = serializers.SerializerMethodField()
    class Meta:
        model = ChatModel
        fields = ['id', 'name', 'created_at','message_num']

    def get_message_num(self, obj):
        # 获取关联的消息数量
        return obj.messages.all().count()


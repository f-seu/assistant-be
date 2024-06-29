from rest_framework import serializers
from .models import ChatModel, MessageModel


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'chat', 'role', 'content', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        # 从kwargs中提取fields参数，如果未指定则为None
        fields = kwargs.pop('fields', [])
        super(ChatSerializer, self).__init__(*args, **kwargs)

        # 如果fields参数被提供，删除不在fields中的所有字段

        allowed = set(fields)
        existing = set(self.fields.keys())
        for field_name in existing - allowed:
            self.fields.pop(field_name)

    class Meta:
        model = ChatModel
        fields = ['id', 'name', 'created_at', 'messages']

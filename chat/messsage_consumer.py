import asyncio
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
import json

from django.shortcuts import get_object_or_404

from chat.models import ChatModel, MessageModel
from utils.chat import ChatService


class MessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_service_obj = None

    def connect(self):
        self.chat_service_obj = ChatService()
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        self.handle_message(text_data)

    @database_sync_to_async
    def get_chat(self, chat_id):
        try:
            return ChatModel.objects.get(id=chat_id)
        except ChatModel.DoesNotExist:
            return None

    def save_message(self, chat, role, content):
        return MessageModel.objects.create(chat=chat, role=role, content=content)

    def get_chat_history(self, chat):
        return list(chat.messages.all().order_by('timestamp').values("role", "content"))

    def handle_message(self, message):
        data = json.loads(message)

        response = dict()
        chat_id = data.get('chatid')
        message_content = data.get('message')

        if not chat_id or not message_content:
            response['msg'] = "chatid and message parameters are required."
            response['code'] = 4001
            self.send(json.dumps(response))

        chat = get_object_or_404(ChatModel, id=chat_id)
        cur_message = MessageModel(chat=chat, role="user", content=message_content)
        cur_message.save()

        history_model = chat.messages.all().order_by('timestamp')
        history = list()
        for h in history_model:
            history.append({"role": h.role, "content": h.content})

        full_text = ""
        for message in self.chat_service_obj.chat_stream(history, message_content):

            full_text += message
            message_obj = {"text": message}
            json_message = json.dumps(message_obj)
            self.send(json_message)

        MessageModel(chat=chat, role="assistant", content=full_text).save()


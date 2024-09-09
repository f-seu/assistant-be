"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatModel, MessageModel
from .serializers import ChatSerializer, MessageSerializer
from utils.chat import ChatService
import json
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

chat_service_obj = ChatService()


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class MessageView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        # 获取一个chat的所有消息列表
        response = dict()
        chat_id = request.query_params.get('chatid')

        if not chat_id:
            response['msg'] = "chatid parameter is required."
            response['code'] = 4001
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)
        messages = chat.messages.all().order_by('timestamp')

        serializer = MessageSerializer(messages, many=True)
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)

    def post(self, request):
        # 发送消息
        response = dict()
        chat_id = request.data.get('chatid')
        message_content = request.data.get('message')

        if not chat_id or not message_content:
            response['msg'] = "chatid and message parameters are required."
            response['code'] = 4001
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)
        cur_message = MessageModel(chat=chat, role="user", content=message_content)
        cur_message.save()

        history_model = chat.messages.all().order_by('timestamp')
        history = list()
        for h in history_model:
            history.append({"role": h.role, "content": h.content})

        def event_stream():
            full_text = ""
            for message in chat_service_obj.chat_stream(history, message_content):

                full_text += message
                message_obj = {"text": message}
                # 转换 message_obj 为 JSON 字符串
                json_message = json.dumps(message_obj)
                # 正确格式化 SSE 消息
                resp = f"data: {json_message}\n\n"
                yield resp
            MessageModel(chat=chat, role="assistant", content=full_text).save()

            # 创建StreamingHttpResponse对象，使用event_stream作为数据源

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response


class ChatView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, format=None):
        # 获取一个chat的所有消息列表
        response = dict()
        chat_id = request.query_params.get('chatid')

        if not chat_id:
            response['msg'] = "chatid parameter is required."
            response['code'] = 4001
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)

        serializer = ChatSerializer(chat, fields=['id', 'name', 'created_at'])
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)

    def post(self, request):
        # 新建一个聊天
        response = dict()
        first_message_content = request.data.get('message')

        if not first_message_content:
            response['msg'] = "message parameter is required."
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"下面是用户输入的一个问题，请不要回答这个问题，而是为这个问题取一个简短的10个字左右的标题:{first_message_content}"
        title = chat_service_obj.chat([], prompt)
        chat = ChatModel(name=title)
        chat.save()

        serializer = ChatSerializer(chat, fields=['id', 'name', 'created_at'])
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)


class ChatListView(APIView):
    def get(self, request):
        response = dict()
        start = request.query_params.get('start', 0)
        end = request.query_params.get('end', None)

        try:
            start = int(start)
            end = int(end) if end is not None else None
        except ValueError:
            response['msg'] = "Invalid start or end parameter"
            response['code'] = 4002
            return Response(response)

        chats = ChatModel.objects.all().order_by('created_at')[start:end]

        serializer = ChatSerializer(chats, many=True, fields=['id', 'name', 'created_at'])
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)


class ChatNumView(APIView):
    def get(self, request, format=None):
        # 获取消息列表，start和end是分页
        response = dict()

        num = ChatModel.objects.all().count()

        response['data'] = num
        response['code'] = 0
        return Response(response)

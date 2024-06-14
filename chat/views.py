from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatModel, MessageModel
from .serializers import ChatSerializer, MessageSerializer


def get_reply(message: list[str]) -> str:
    # 简单的回复函数，可以根据需要进行扩展
    return "This is a reply to your message."


class MessageView(APIView):
    def get(self, request, format=None):
        response = dict()
        chat_id = request.query_params.get('chatid')

        if not chat_id:
            response['messages'] = "chatid parameter is required."
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)
        messages = chat.messages.all().order_by('timestamp')

        serializer = MessageSerializer(messages, many=True)
        response['messages'] = serializer.data
        response['code'] = 0
        return Response(response)

    def post(self, request, format=None):
        response = dict()
        chat_id = request.data.get('chatid')
        message_content = request.data.get('message')

        if not chat_id or not message_content:
            response['messages'] = "chatid and message parameters are required."
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)
        message = MessageModel(chat=chat, sender="User", content=message_content)
        message.save()

        reply_content = get_reply([message_content])
        reply_message = MessageModel(chat=chat, sender="AI", content=reply_content)
        reply_message.save()

        response['messages'] = MessageSerializer(reply_message).data
        response['code'] = 0
        return Response(response)


class ChatView(APIView):
    def get(self, request, format=None):
        response = dict()
        start = request.query_params.get('start', 0)
        end = request.query_params.get('end', None)

        try:
            start = int(start)
            end = int(end) if end is not None else None
        except ValueError:
            response['messages'] = "Invalid start or end parameter"
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chats = ChatModel.objects.all().order_by('created_at')[start:end]

        serializer = ChatSerializer(chats, many=True)
        response['messages'] = serializer.data
        response['code'] = 0
        return Response(response)

    def post(self, request, format=None):
        response = dict()
        first_message_content = request.data.get('message')

        if not first_message_content:
            response['messages'] = "message parameter is required."
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = ChatModel(name="New Chat")
        chat.save()

        first_message = MessageModel(chat=chat, sender="User", content=first_message_content)
        first_message.save()

        reply_content = get_reply([first_message_content])
        reply_message = MessageModel(chat=chat, sender="AI", content=reply_content)
        reply_message.save()

        response['messages'] = ChatSerializer(chat).data
        response['code'] = 0
        return Response(response)


from django.http import StreamingHttpResponse
import time
import json


def sse_service(request):
    # 使用StreamingHttpResponse进行SSE响应
    response = StreamingHttpResponse(stream_content(),
                                     content_type="text/event-stream")
    return response


def stream_content():
    # 这里可以是你的数据库查询或长轮询逻辑
    while True:
        time.sleep(5)  # 模拟长轮询延迟
        yield "data: %s\n\n" % json.dumps({"message": "Hello, SSE!"})

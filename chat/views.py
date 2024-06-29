from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatModel, MessageModel
from .serializers import ChatSerializer, MessageSerializer
from .chat_service import ChatService
import json

chat_service_obj = ChatService()


class MessageView(APIView):
    def get(self, request, format=None):
        # 获取一个chat的所有消息列表
        response = dict()
        chat_id = request.query_params.get('chatid')

        if not chat_id:
            response['messages'] = "chatid parameter is required."
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
            response['messages'] = "chatid and message parameters are required."
            response['code'] = 4001
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)
        cur_message = MessageModel(chat=chat, role="user", content=message_content)
        cur_message.save()

        history_model = chat.messages.all().order_by('timestamp')
        history = list()
        for h in history_model:
            history.append({"role": h.role, "content": h.content})
        print(history)

        def event_stream():
            full_text = ""
            for message in chat_service_obj.chat(history, message_content):
                full_text += message['text']
                yield f"data: {json.dumps(message)}\n\n"
            MessageModel(chat=chat, role="assistant", content=full_text).save()

            # 创建StreamingHttpResponse对象，使用event_stream作为数据源

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response


class ChatView(APIView):
    def get(self, request, format=None):
        # 获取一个chat的所有消息列表
        response = dict()
        chat_id = request.query_params.get('chatid')

        if not chat_id:
            response['messages'] = "chatid parameter is required."
            response['code'] = 4001
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(ChatModel, id=chat_id)

        serializer = ChatSerializer(chat, fields=['id', 'name', 'created_at'])
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)

    def post(self, request, format=None):
        # 新建一个聊天
        response = dict()
        first_message_content = request.data.get('message')

        if not first_message_content:
            response['messages'] = "message parameter is required."
            response['code'] = 1
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        title = chat_service_obj.get_title(first_message_content)
        chat = ChatModel(name=title)
        chat.save()

        first_message = MessageModel(chat=chat, role="user", content=first_message_content)
        first_message.save()

        def event_stream():
            full_text = ""
            first_response_obj = {"chatid": chat.id, "title": title}
            yield f'data: {json.dumps(first_response_obj)}\n\n'
            for message in chat_service_obj.chat([], first_message_content):
                full_text += message['text']
                yield f"data: {json.dumps(message)}\n\n"
            MessageModel(chat=chat, role="assistant", content=full_text).save()

            # 创建StreamingHttpResponse对象，使用event_stream作为数据源

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response


class ChatListView(APIView):
    def get(self, request):
        response = dict()
        start = request.query_params.get('start', 0)
        end = request.query_params.get('end', None)

        try:
            start = int(start)
            end = int(end) if end is not None else None
        except ValueError:
            response['messages'] = "Invalid start or end parameter"
            response['code'] = 4002
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        chats = ChatModel.objects.all().order_by('created_at')[start:end]

        serializer = ChatSerializer(chats, many=True,fields=['id', 'name', 'created_at'])
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

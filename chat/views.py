from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class ChatView(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        response = dict()
        response['messages'] = "success"
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
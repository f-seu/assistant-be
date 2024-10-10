from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from assistant_be.settings import BACKEND_URL
from django.http import HttpResponsePermanentRedirect


class UserView(APIView):
    def get(self, request):
        pass

    def put(self, request):
        pass


import requests
from django.http import HttpResponse


def proxy_view(request, target_url):
    # 从原始请求中提取数据
    method = request.method
    headers = {key: value for key, value in request.headers.items() if key != 'Host'}
    params = request.GET  # 查询参数
    data = request.body  # 请求体内容

    # 根据请求类型做相应的转发
    print(method)
    if method == 'GET':
        response = requests.get(target_url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(target_url, headers=headers, data=data)
    elif method == 'PUT':
        response = requests.put(target_url, headers=headers, data=data)
    elif method == 'DELETE':
        response = requests.delete(target_url, headers=headers, data=data)
        print(response)
    else:
        return HttpResponse(status=405)  # 方法不允许

    # 将目标服务器的响应返回给用户
    django_response = HttpResponse(
        content=response.content,
        status=response.status_code
    )

    # 将目标服务器的响应头也复制到Django的响应中
    for key, value in response.headers.items():
        django_response[key] = value

    return django_response

@require_http_methods(["GET"])
def get_file_list(request):
    target_url = f"{BACKEND_URL}knowledge_base/list_files"
    return proxy_view(request, target_url)

@csrf_exempt
@require_http_methods(["POST"])
def delete_file(request):
    print("XXXX")
    target_url = f"{BACKEND_URL}knowledge_base/delete_docs"
    return proxy_view(request, target_url)


@csrf_exempt
@require_http_methods(["POST"])
def post_file(request):
    target_url = f"{BACKEND_URL}knowledge_base/upload_docs"
    return proxy_view(request, target_url)

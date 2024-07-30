from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import threading
from .models import RecommendModel
from .serializers import RecommendModelSerializer
from .service import RecommendService
import logging

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

# Create your views here.
class RecommendView(APIView):
    logger = logging.getLogger('myapp')
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    service = RecommendService()

    def get(self, request):
        response = dict()
        response['code'] = 0
        recommend_type = request.query_params.get('type')
        if recommend_type is None:
            response['code'] = 4001
            response['msg'] = "缺少请求参数type"
            return Response(response)
        if recommend_type not in ("music", "movie"):
            response['code'] = 4001
            response['msg'] = "type只能为music或者movie"
            return Response(response)

        # 启动线程进行推荐计算
        thread = threading.Thread(target=self.get_recommend, args=(recommend_type,), daemon=True)
        thread.start()

        latest_recommendation = RecommendModel.objects.filter(recommend_type=recommend_type).order_by('-create_at').first()
        print(latest_recommendation)
        if latest_recommendation:
            response['data'] = RecommendModelSerializer(latest_recommendation).data
        else:
            response['code'] = 4004
            response['msg'] = "暂无推荐，请您稍后重试"

        return Response(response)

    def get_recommend(self, recommend_type):
        if cache.get(recommend_type):
            return
        self.logger.info(f"开始推荐 {recommend_type}")
        cache.set(recommend_type, "true", timeout=300)
        MAX_RETRIES = 5
        for t in range(MAX_RETRIES):
            try:
                if recommend_type == "music":
                    result = self.service.get_music(5)
                elif recommend_type == "movie":
                    result = self.service.get_movie(5)
                else:
                    cache.delete(recommend_type)
                    return
                print(result)
                recommend_obj = RecommendModel.objects.create(recommend_type=recommend_type, content=result)
                recommend_obj.save()
                break
            except Exception as err:
                self.logger.error(f"获取推荐失败: {err}，正在重试{t}")
        cache.delete(recommend_type)

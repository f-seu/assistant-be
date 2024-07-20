from django.shortcuts import render

# Create your views here.
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import CalendarModel, PlanModel
from .service import CalendarService
from .serializers import CalenderSerializer, PlanSerializer, PlanParamsSerializer
import re
from django.core.cache import cache
import threading
import logging

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class CalendarView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        response = dict()
        response['code'] = 0
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        day = request.query_params.get('day')
        if not year or not month or not day:
            response['msg'] = "参数错误"
            response['code'] = 4001
            return Response(response, status=status.HTTP_200_OK)
        calender = CalendarModel.objects.filter(year=year, month=month, day=day).first()
        if not calender:
            calender = CalendarModel.objects.create(year=year, month=month, day=day)
            calender.save()
        serializer = CalenderSerializer(calender)
        response['data'] = serializer.data
        response['code'] = 0
        return Response(response)

    def put(self, request):
        response = dict()
        response['code'] = 0
        year = request.data.get('year')
        month = request.data.get('month')
        day = request.data.get('day')
        content = request.data.get('content')
        if not year or not month or not day or not content:
            response['msg'] = "参数错误"
            response['code'] = 4001
            return Response(response, status=status.HTTP_200_OK)
        calender = CalendarModel.objects.filter(year=year, month=month, day=day).first()
        if not calender:
            calender = CalendarModel.objects.create(year=year, month=month, day=day)
            calender.save()
        calender.content = content
        calender.save()
        response['code'] = 0
        return Response(response)


class PlanView(APIView):
    logger = logging.getLogger('myapp')
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    calender_service = CalendarService()

    def get(self, request):
        # 获取一个chat的所有消息列表
        response = dict()
        response['code'] = 0
        serializer = PlanParamsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'code': 4001, 'msg': '参数错误'})

        data = serializer.validated_data
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        force_update = data.get('force_update')

        if cache.get(f"{year}-{month}-{day}"):
            response['code'] = 2002
            response['msg'] = "日程正在规划中，请您稍后尝试"
            return Response(response)

        plan, _ = PlanModel.objects.get_or_create(year=year, month=month, day=day)
        if force_update or plan.content == "":
            calender = CalendarModel.objects.filter(year=year,month=month,day=day).first()
            if calender is None or len(calender.content) < 10:
                self.logger.warning(f"规划{year}-{month}-{day}日程失败，calender对象：{calender}")
                response['msg'] = "当前选择日期不存在日程或日程过短，无法进行规划"
                response['code'] = 4002
                return Response(response)

            thread = threading.Thread(target=self.get_plan, args=(year, month, day, calender.content),daemon=True)
            thread.start()
            response['code'] = 2002
            response['msg'] = "日程正在规划中，请您稍后尝试"
            return Response(response)

        else:
            response['data'] = PlanSerializer(plan).data
            return Response(response)

    def get_plan(self, year, month, day, content):
        cache.set(f"{year}-{month}-{day}","true", timeout=300)
        try:
            plan_str = self.calender_service.get_plan(year=year, month=month, day=day, content=content)
            pattern = r'"action": "Final Answer",\s*"action_input":\s*"([^"]+)"'
            matches = re.findall(pattern, plan_str)
            plan_str = matches[0]
            plan = PlanModel.objects.get(year=year, month=month, day=day)
            plan.content = plan_str
            plan.save()
        except Exception as err:
            self.logger.error(f"获取日程失败:{err}")
        cache.delete(f"{year}-{month}-{day}")

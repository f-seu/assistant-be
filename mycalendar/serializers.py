"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from rest_framework import serializers
from .models import CalendarModel,PlanModel


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarModel
        fields = ['id', 'content','update_at','user_update']

class CalendarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarModel
        fields = ['id', 'day']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        fields = ['id', 'content','update_at','has_processed']


class PlanParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    day = serializers.IntegerField(required=True)

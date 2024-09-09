"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from rest_framework import serializers
from .models import CalendarModel,PlanModel


class CalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarModel
        fields = ['id', 'content']


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        fields = ['id', 'content']


class PlanParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    day = serializers.IntegerField(required=True)
    force_update = serializers.BooleanField(required=True)
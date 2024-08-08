from rest_framework import serializers
from .models import CalenderModel,PlanModel


class CalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalenderModel
        fields = ['id', 'content']

class CalenderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalenderModel
        fields = ['id', 'day']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        fields = ['id', 'content']


class PlanParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    day = serializers.IntegerField(required=True)
    force_update = serializers.BooleanField(required=True)
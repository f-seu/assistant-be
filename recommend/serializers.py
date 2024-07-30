from rest_framework import serializers
from .models import RecommendModel
import json

class RecommendModelSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = RecommendModel
        fields = ['create_at', 'recommend_type', 'content']

    def get_content(self, obj):
        return json.loads(obj.content)
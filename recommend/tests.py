from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import RecommendModel
from datetime import timedelta
from django.utils.timezone import now

class RecommendViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-recommend')

        # 创建音乐推荐的示例数据
        RecommendModel.objects.create(
            recommend_type='music',
            content={"songs": [{"title": "Song A", "artist": "Artist X"}]}
        )

        # 创建电影推荐的示例数据
        RecommendModel.objects.create(
            recommend_type='movie',
            content={"movies": [{"title": "Movie A", "director": "Director Y"}]}
        )

    def test_recommend_view_without_type(self):
        """ 测试不带type参数的请求 """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('缺少请求参数type', response.data['msg'])

    def test_recommend_view_invalid_type(self):
        """ 测试带有无效type参数的请求 """
        response = self.client.get(self.url, {'type': 'game'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type只能为music或者movie', response.data['msg'])

    def test_recommend_view_with_valid_type(self):
        """ 测试有效的type参数请求 """
        response = self.client.get(self.url, {'type': 'music'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Song A', response.data['data']['content']['songs'][0]['title'])

    def test_recommendation_update_trigger(self):
        """ 测试推荐更新触发逻辑 """
        # 假设最近的推荐已经超过1分钟
        old_recommendation = RecommendModel.objects.get(recommend_type='music')
        old_recommendation.create_at -= timedelta(minutes=2)
        old_recommendation.save()

        response = self.client.get(self.url, {'type': 'music'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], '日程正在规划中，请您稍后尝试')

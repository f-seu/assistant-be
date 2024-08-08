from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import CalenderModel, PlanModel
from datetime import datetime

class CalenderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.calender = CalenderModel.objects.create(year=2022, month=7, day=20, content="Meeting at noon")
        self.url = reverse('calender')

    def test_get_calender(self):
        response = self.client.get(self.url, {'year': '2022', 'month': '7', 'day': '20'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Meeting at noon")

    def test_put_calender(self):
        response = self.client.put(self.url, {'year': '2022', 'month': '7', 'day': '20', 'content': "Updated meeting"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.calender.refresh_from_db()
        self.assertEqual(self.calender.content, "Updated meeting")

class HasCalenderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        CalenderModel.objects.create(year=2022, month=7, day=21, content="Doctor's appointment")
        self.url = reverse('has-calender')

    def test_get_has_calender(self):
        response = self.client.get(self.url, {'year': '2022', 'month': '7'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Doctor's appointment")

class PlanViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.plan = PlanModel.objects.create(year=2022, month=7, day=22, content="Plan for vacation")
        self.url = reverse('plan')

    def test_get_plan(self):
        response = self.client.get(self.url, {'year': '2022', 'month': '7', 'day': '22', 'force_update': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Plan for vacation")

    def test_update_plan(self):
        response = self.client.get(self.url, {'year': '2022', 'month': '7', 'day': '22', 'force_update': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertIn("Plan for vacation", self.plan.content)

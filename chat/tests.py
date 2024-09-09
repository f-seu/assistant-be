"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import ChatModel, MessageModel
from datetime import datetime

class ChatModelTestCase(TestCase):
    def setUp(self):
        self.chat = ChatModel.objects.create(name="Test Chat")

    def test_chat_creation(self):
        self.assertIsInstance(self.chat, ChatModel)
        self.assertEqual(self.chat.name, "Test Chat")

class MessageModelTestCase(TestCase):
    def setUp(self):
        self.chat = ChatModel.objects.create(name="Test Chat")
        self.message = MessageModel.objects.create(
            chat=self.chat,
            role="user",
            content="Hello, this is a test message.",
            timestamp=datetime.now()
        )

    def test_message_creation(self):
        self.assertIsInstance(self.message, MessageModel)
        self.assertEqual(self.message.chat, self.chat)
        self.assertEqual(self.message.role, "user")
        self.assertEqual(self.message.content, "Hello, this is a test message.")

class ChatViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.chat = ChatModel.objects.create(name="Test Chat")
        self.url = reverse('api/chat/', kwargs={'chatid': self.chat.id})

    def test_get_chat(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Chat")

    def test_delete_chat(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChatModel.objects.count(), 0)

class ChatListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        ChatModel.objects.create(name="Test Chat 1")
        ChatModel.objects.create(name="Test Chat 2")
        self.url = reverse('api/chat-list/')

    def test_list_chats(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class ChatNumViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        ChatModel.objects.create(name="Test Chat")
        self.url = reverse('api/chat-num')

    def test_num_chats(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], 1)

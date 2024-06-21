from django.db import models

# Create your models here.
class ChatModel(models.Model):
    class Meta:
        db_table = "chat"
        verbose_name = "聊天"
        verbose_name_plural = verbose_name
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MessageModel(models.Model):
    class Meta:
        db_table = "message"
        verbose_name = "消息"
        verbose_name_plural = verbose_name
    chat = models.ForeignKey(ChatModel, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:20]}..."


"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.db import models
import json
from django.utils.timezone import now

class RecommendModel(models.Model):
    class Meta:
        db_table = "recommend"
        verbose_name = "推荐"
        verbose_name_plural = verbose_name

    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    recommend_type = models.CharField(max_length=50, verbose_name="推荐类型", choices=(("music", "Music"), ("movie", "Movie"),("app","App")))
    content = models.JSONField(verbose_name="内容")

    def __str__(self):
        return f"{self.create_at} - {self.recommend_type}"


class AppOpenModel(models.Model):
    class Meta:
        db_table = "app_open"
        verbose_name = "app打开记录"
        verbose_name_plural = verbose_name

    create_at = models.DateTimeField(default=now, verbose_name="打开时间")
    name = models.CharField(max_length=255,verbose_name="名称")

    def __str__(self):
        return f"{self.create_at} - {self.name}"

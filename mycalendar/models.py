"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.db import models


# Create your models here.
class CalendarModel(models.Model):
    class Meta:
        db_table = "calendar"
        verbose_name = "日程"
        verbose_name_plural = verbose_name

    year = models.PositiveSmallIntegerField(verbose_name="年")
    month = models.PositiveSmallIntegerField(verbose_name="月")
    day = models.PositiveSmallIntegerField(verbose_name="日")
    content = models.TextField(verbose_name="日程")
    update_at = models.DateTimeField(auto_now=True, verbose_name="最后更新日期")
    user_update = models.BooleanField(verbose_name="由用户更新", default=False)
    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}:{str(self.content)}"

class PlanModel(models.Model):
    class Meta:
        db_table = "plan"
        verbose_name = "规划"
        verbose_name_plural = verbose_name

    year = models.PositiveSmallIntegerField(verbose_name="年")
    month = models.PositiveSmallIntegerField(verbose_name="月")
    day = models.PositiveSmallIntegerField(verbose_name="日")
    content = models.TextField(verbose_name="规划后日程")
    has_processed = models.BooleanField(verbose_name="是否已经处理过", default=False)
    update_at = models.DateTimeField(auto_now=True, verbose_name="最后更新日期")

    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}:{str(self.content)}"



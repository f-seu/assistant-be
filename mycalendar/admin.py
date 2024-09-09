"""
 * Copyright (c) 2024, Li Yaning,Zu Yuankun/Southeast University
 * Licensed under the GPL3 License (see LICENSE file for details)
"""

from django.contrib import admin
from .models import CalendarModel,PlanModel

@admin.register(CalendarModel)
class CalenderModelAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'day', 'content')
    list_filter = ('year', 'month', 'day')
    search_fields = ('content',)


@admin.register(PlanModel)
class PlanModelAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'day', 'content', 'last_modified')
    list_filter = ('year', 'month', 'day')
    search_fields = ('content',)


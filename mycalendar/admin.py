from django.contrib import admin
from .models import CalendarModel,PlanModel

@admin.register(CalendarModel)
class CalendarModelAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'day', 'content')
    list_filter = ('year', 'month', 'day')
    search_fields = ('content',)


@admin.register(PlanModel)
class PlanModelAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'day', 'content', 'last_modified')
    list_filter = ('year', 'month', 'day')
    search_fields = ('content',)


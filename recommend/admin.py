from django.contrib import admin
from .models import RecommendModel

@admin.register(RecommendModel)
class RecommendModelAdmin(admin.ModelAdmin):
    list_display = ('create_at','recommend_type')


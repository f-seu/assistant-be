from django.contrib import admin
from .models import RecommendModel, AppOpenModel
from django import forms


@admin.register(RecommendModel)
class RecommendModelAdmin(admin.ModelAdmin):
    list_display = ('create_at', 'recommend_type')


class AppOpenModelForm(forms.ModelForm):
    class Meta:
        model = AppOpenModel
        fields = '__all__'  # 确保所有字段都包含在内
        widgets = {
            'create_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


@admin.register(AppOpenModel)
class AppOpenModelAdmin(admin.ModelAdmin):
    list_display = ('create_at', 'name')

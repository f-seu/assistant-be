from django.db import models
import json

class RecommendModel(models.Model):
    class Meta:
        db_table = "recommend"
        verbose_name = "推荐"
        verbose_name_plural = verbose_name

    create_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    recommend_type = models.CharField(max_length=50, verbose_name="推荐类型", choices=(("music", "Music"), ("movie", "Movie")))
    content = models.JSONField(verbose_name="内容")

    def __str__(self):
        return f"{self.create_at} - {self.recommend_type}"

from django.db import models


class TimeStampedModel(models.Model):

    "Time Stamp Model"
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # 이거 해줘야 데이터베이스에서 모델안만듬

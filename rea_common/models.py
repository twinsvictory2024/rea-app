import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name='Дата обновления',
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at'])
        ]


class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Первичный ключ'
    )

    class Meta:
        abstract = True
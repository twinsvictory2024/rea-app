from django.db import models
from rea_common.models import TimeStampedModel, UUIDModel
from rea_users.models import CustomUser

class Shop(TimeStampedModel, UUIDModel):
    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.PROTECT,
        related_name='shop',
        verbose_name='Пользователь'
    )

    label = models.CharField(
        max_length=50,
        verbose_name='Название'
    )

    active = models.BooleanField(
        default=True,
        verbose_name='Принимает заказы'
    )

    class Meta:
        verbose_name = 'Магазин'
        ordering = ['-created_at']

    def __str__(self):
        return self.label
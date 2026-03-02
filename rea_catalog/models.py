from django.db import models
from rea_common.models import TimeStampedModel, UUIDModel
from rea_vendors.models import Shop

class Category(TimeStampedModel, UUIDModel):
    label = models.CharField(
        max_length=40,
        verbose_name='Название'
    )

    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True
    )

    class Meta:
        verbose_name = 'Категория'
        ordering = ['-created_at']

    def __str__(self):
        return self.label
    
class Product(TimeStampedModel, UUIDModel):
    label = models.CharField(
        max_length=80,
        verbose_name='Название'
    )

    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
    )

    model = models.CharField(
        max_length=80,
        verbose_name='Модель',
        blank=True
    )

    ext_id = models.CharField(
        verbose_name='Внешний ИД'
    )

    shop = models.ForeignKey(
        Shop, verbose_name='Магазин',
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )

    stock = models.PositiveIntegerField(
        verbose_name='Количество на складе'
    )

    price = models.PositiveIntegerField(
        verbose_name='Цена'
    )

    price_rrc = models.PositiveIntegerField(
        verbose_name='Рекомендуемая розничная цена'
    )

    class Meta:
        verbose_name = 'Продукт'
        ordering = ['-created_at']

    def __str__(self):
        return self.label
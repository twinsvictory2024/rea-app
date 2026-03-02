from django.db import models
from rea_common.models import TimeStampedModel, UUIDModel
from rea_catalog.models import Product

class Parameter(TimeStampedModel, UUIDModel):
    label = models.CharField(
        max_length=40,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Имя параметра'
        ordering = ['-created_at']

    def __str__(self):
        return self.label


class ProductParameter(UUIDModel):
    product = models.ForeignKey(
        Product,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )

    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Параметр',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )

    value = models.CharField(
        verbose_name='Значение',
        max_length=100
    )

    class Meta:
        verbose_name = 'Параметр'
        constraints = [
            models.UniqueConstraint(fields=['product', 'parameter'], name='unique_product_parameter'),
        ]
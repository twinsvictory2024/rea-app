from django.db import models
from django.db.models import Sum, F
from rea_common.models import TimeStampedModel, UUIDModel
from rea_users.models import CustomUser, Contact
from rea_catalog.models import Product

class Order(TimeStampedModel, UUIDModel):
    STATE_BASKET = 'basket'
    STATE_NEW = 'new'
    STATE_CONFIRMED = 'confirmed'
    STATE_ASSEMBLED = 'assembled'
    STATE_SENT = 'sent'
    STATE_DELIVERED = 'delivered'
    STATE_CANCELED = 'canceled'

    STATE_CHOICES = (
        (STATE_BASKET, 'Статус корзины'),
        (STATE_NEW, 'Новый'),
        (STATE_CONFIRMED, 'Подтвержден'),
        (STATE_ASSEMBLED, 'Собран'),
        (STATE_SENT, 'Отправлен'),
        (STATE_DELIVERED, 'Доставлен'),
        (STATE_CANCELED, 'Отменен')
    )

    state = models.CharField(
        choices=STATE_CHOICES,
        default=STATE_BASKET,
        max_length=15,
        verbose_name='Статус'
    )

    user = models.ForeignKey(
        CustomUser, 
        related_name='orders',
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='Пользователь'
    )

    contact = models.ForeignKey(
        Contact,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Контакт'
    )

    class Meta:
        verbose_name = 'Заказ'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.created_at)
    
    @property
    def total_price(self):
        total = self.order_items.aggregate(
            total=Sum(F('product__price') * F('qty'))
        )['total']
        return total or 0
    
    @property
    def total_price_display(self):
        return f"{self.total_price:.2f} ₽"
    
    @property
    def items_count(self):
        return self.order_items.aggregate(
            total=Sum('qty')
        )['total'] or 0
    
    def check_stock(self):
        insufficient_items = []
        
        for item in self.order_items.select_related('product'):
            if item.product.stock < item.qty:
                insufficient_items.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,  # предполагаю что есть поле name
                    'requested': item.qty,
                    'available': item.product.stock
                })
        
        return len(insufficient_items) == 0, insufficient_items
    
    def reserve_stock(self):
        for item in self.order_items.select_related('product'):
            product = item.product
            product.stock -= item.qty
            product.save()
    
    def release_stock(self):
        for item in self.order_items.select_related('product'):
            product = item.product
            product.stock += item.qty
            product.save()


class OrderItem(TimeStampedModel, UUIDModel):
    order = models.ForeignKey(
        Order,
        related_name='order_items',
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )

    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='order_items',
        blank=True,
        on_delete=models.PROTECT
    )

    qty = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Заказанная позиция'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product'], name='unique_order_item'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return str(self.created_at)
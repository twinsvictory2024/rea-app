from rest_framework import serializers
from ..models import Order
from rea_users.serializers.contact import ContactSerializer
from ..serializers.order_item import OrderItemSerializer
from rea_common.mixins import TimestampSerializerMixin

class OrderSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    order_items = OrderItemSerializer(read_only=True, many=True)
    contact = ContactSerializer(read_only=True, many=False)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    total_price_display = serializers.CharField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'state',
            'order_items',
            'contact',
            'total_price',
            'total_price_display',
            'items_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'state', 'created_at', 'updated_at', 
                           'total_price', 'total_price_display', 'items_count']
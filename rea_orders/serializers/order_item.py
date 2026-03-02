from rest_framework import serializers
from ..models import OrderItem
from rea_catalog.serializers.product import ProductShortSerializer
from rea_common.mixins import TimestampSerializerMixin
from rea_users.serializers.contact import ContactSerializer

class OrderItemSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True, many=False)
    price = serializers.DecimalField(
        source='product.price', 
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'qty',
            'product',
            'price',
            'total_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.qty * obj.product.price
    

class OrderItemVendorSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    customer_name = serializers.CharField(source='order.user.full_name', read_only=True)
    customer_email = serializers.EmailField(source='order.user.email', read_only=True)
    order_date = serializers.DateTimeField(source='order.created_at', read_only=True)
    order_state = serializers.CharField(source='order.state', read_only=True)
    contact_info = ContactSerializer(source='order.contact', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'qty',
            'product',
            'customer_name',
            'customer_email',
            'order_date',
            'order_state',
            'contact_info',
            'created_at'
        ]
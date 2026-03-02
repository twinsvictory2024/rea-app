from rest_framework import serializers
from ..models import Product
from rea_common.mixins import TimestampSerializerMixin
from rea_eav.serializers.product_parameter import ProductParameterSerializer

class ProductSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'label',
            'category',
            'model',
            'stock',
            'price',
            'price_rrc',
            'product_parameters',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductListSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'label',
            'category',
            'model',
            'stock',
            'price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'label',
            'price',
        ]
        read_only_fields = ['id']
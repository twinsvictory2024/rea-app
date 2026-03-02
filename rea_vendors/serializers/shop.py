from rest_framework import serializers
from ..models import Shop
from rea_common.mixins import TimestampSerializerMixin


class ShopSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'id',
            'user',
            'label',
            'active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
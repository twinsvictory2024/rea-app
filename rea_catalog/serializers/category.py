from rest_framework import serializers
from ..models import Category
from rea_common.mixins import TimestampSerializerMixin

class CategorySerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'label',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
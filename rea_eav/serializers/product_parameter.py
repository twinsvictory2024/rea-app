from rest_framework import serializers
from ..models import ProductParameter

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = [
            'parameter',
            'value'
        ]
        read_only_fields = ['id']
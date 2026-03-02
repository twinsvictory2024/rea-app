from rest_framework import serializers
from ..models import Contact
from rea_common.mixins import TimestampSerializerMixin

class ContactSerializer(TimestampSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'city',
            'street',
            'house',
            'structure',
            'building',
            'apartment',
            'phone',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

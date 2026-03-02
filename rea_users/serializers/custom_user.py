from rest_framework import serializers
from ..models import CustomUser
from rea_common.mixins import TimestampSerializerMixin


class CustomUserSerializer(TimestampSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'role',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomUserShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'email'
        ]
        read_only_fields = ['id']
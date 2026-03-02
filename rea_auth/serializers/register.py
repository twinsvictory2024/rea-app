from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rea_users.models import CustomUser
from rea_users.serializers.custom_user import CustomUserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'patronymic',
            'password',
            'password_confirm',
            'role'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        user_data = {
            'email': validated_data['email'],
            'password': validated_data['password'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'patronymic': validated_data.get('patronymic', ''),
        }
        
        if 'role' in validated_data:
            user_data['role'] = validated_data['role']
        
        user = CustomUser.objects.create_user(**user_data)
        return user
        
    def to_representation(self, instance):
        return CustomUserSerializer(instance, context=self.context).data
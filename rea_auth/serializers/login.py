from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rea_users.models import CustomUser
from rea_users.serializers.custom_user import CustomUserSerializer


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def to_representation(self, instance):
        return CustomUserSerializer(instance, context=self.context).data
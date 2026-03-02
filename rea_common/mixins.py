from rest_framework import serializers


class TimestampSerializerMixin(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%d.%m.%Y в %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%d.%m.%Y в %H:%M")

from rest_framework import serializers
from .models import Password

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("Password cannot be empty.")
        return value

    def update(self, instance, validated_data):
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance

class ServicesAndPasswordsSerializer(PasswordSerializer):
    service_name = serializers.CharField(required=True)

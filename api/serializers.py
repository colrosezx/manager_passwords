from django.forms import ValidationError
from rest_framework import serializers
from .models import Password

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate(self, data):
        try:
            instance = Password(**data)
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def update(self, instance, validated_data):
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance

class ServicesAndPasswordsSerializer(PasswordSerializer):
    service_name = serializers.CharField(required=True)

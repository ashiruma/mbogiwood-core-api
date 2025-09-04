# users/serializers.py
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(BaseUserSerializer):
    """
    Serializer for displaying a user's public information.
    """
class Meta(BaseUserSerializer.Meta):
    model = User
    fields = ['id', 'email', 'full_name', 'role']


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for creating a new user. It uses Djoser's base
    to handle password hashing and validation securely.
    """
class Meta(BaseUserCreateSerializer.Meta):
    model = User
    fields = ('id', 'email', 'full_name', 'password')
   
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Use the custom manager's create_user method
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        return user
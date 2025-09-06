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
        fields = ["id", "email", "full_name", "role"]


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for creating a new user.
    Adds password confirmation on top of Djoser's defaults.
    """
    password2 = serializers.CharField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "full_name", "password", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn’t match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data.get("full_name"),
            password=validated_data["password"],
        )

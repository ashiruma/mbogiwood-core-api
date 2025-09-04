# reviews/serializers.py
from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer # Assuming you have a simple UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
from rest_framework import serializers
from .models import Review, Rating


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'film', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'film', 'user', 'score', 'created_at']
        read_only_fields = ['user', 'created_at']

# community/serializers.py
from rest_framework import serializers
from .models import Post, Comment, Like, FilmRating
from films.models import Film


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "user", "title", "body", "category", "created_at", "updated_at", "like_count", "comment_count", "comments"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["user"]


class FilmRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FilmRating
        fields = ["id", "user", "film", "rating", "created_at", "updated_at"]


class FilmWithRatingSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Film
        fields = ["id", "title", "description", "poster_url", "average_rating", "rating_count"]

    def get_average_rating(self, obj):
        ratings = obj.ratings.

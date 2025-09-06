# community/serializers.py

from rest_framework import serializers
from .models import Post, Comment, Like, FilmRating

class CommentSerializer(serializers.ModelSerializer):
    # FIXED: Changed source from 'author' to 'user'
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        # FIXED: Fields now match the model ('content' instead of 'body')
        fields = ['id', 'post', 'user', 'user_name', 'content', 'created_at']
        read_only_fields = ['user']

class PostSerializer(serializers.ModelSerializer):
    # FIXED: Changed source from 'author' to 'user'
    user_name = serializers.CharField(source='user.username', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        # FIXED: Fields now match the model ('content' instead of 'body')
        fields = [
            'id', 'title', 'content', 'user', 'user_name', 
            'created_at', 'updated_at', 'comments', 'likes_count'
        ]
        read_only_fields = ['user']

    def get_likes_count(self, obj):
        # This correctly counts the number of related 'like' objects
        return obj.likes.count()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user']

class FilmRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FilmRating
        # FIXED: Removed non-existent 'review' field and fixed field names
        fields = ['id', 'film', 'user', 'user_name', 'score', 'created_at']
        read_only_fields = ['user']
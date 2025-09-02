# filmmakers/serializers.py
from rest_framework import serializers
from .models import FilmmakerApplication

class FilmmakerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmmakerApplication
        fields = ['portfolio_link', 'bio']
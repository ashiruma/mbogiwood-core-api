# about/serializers.py
from rest_framework import serializers
from .models import AboutPageContent, TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'bio', 'image']

class AboutPageSerializer(serializers.Serializer):
    mission_statement = serializers.CharField()
    vision_statement = serializers.CharField() # <-- ADDED
    our_story = serializers.CharField()
    our_values = serializers.CharField() # <-- ADDED
    team_members = TeamMemberSerializer(many=True)
     # --- ADD THESE FIELDS ---
    films_featured = serializers.IntegerField()
    professionals_connected = serializers.CharField()
    countries_reached = serializers.IntegerField()
    hours_watched = serializers.CharField()
    # ------------------------
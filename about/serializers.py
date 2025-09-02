# about/serializers.py
from rest_framework import serializers
from .models import AboutPageContent, TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'bio', 'image']

class AboutPageSerializer(serializers.Serializer):
    mission_statement = serializers.CharField()
    our_story = serializers.CharField()
    team_members = TeamMemberSerializer(many=True)
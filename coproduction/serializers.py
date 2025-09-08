# FILE: coproduction/serializers.py

from rest_framework import serializers
from .models import Project, CollaborationProposal

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['owner']

class CollaborationProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationProposal
        fields = '__all__'
        read_only_fields = ['proposer', 'project']
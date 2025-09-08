# jobs/serializers.py
from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 
            'location', 'description', 'job_type', 'created_at'
        ]
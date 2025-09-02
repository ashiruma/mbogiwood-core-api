# jobs/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Job
from .serializers import JobSerializer

class JobListView(generics.ListAPIView):
    """
    API view to list all active jobs.
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = [AllowAny] # Make this endpoint public
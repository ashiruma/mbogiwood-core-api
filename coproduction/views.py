# FILE: coproduction/views.py

from rest_framework import viewsets, permissions
from .models import Project, CollaborationProposal
from .serializers import ProjectSerializer, CollaborationProposalSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CollaborationProposalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows collaboration proposals to be viewed or edited.
    """
    queryset = CollaborationProposal.objects.all()
    serializer_class = CollaborationProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(proposer=self.request.user)

    def perform_create(self, serializer):
        project = Project.objects.get(pk=self.kwargs['project_pk'])
        serializer.save(proposer=self.request.user, project=project)
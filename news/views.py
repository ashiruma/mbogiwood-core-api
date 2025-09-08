# FILE: news/views.py

from rest_framework import viewsets, permissions
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows articles to be viewed or edited.
    """
    queryset = Article.objects.filter(status=Article.Status.PUBLISHED)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anyone to read, but only authenticated users to create/edit
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
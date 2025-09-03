# filmmakers/views.py
from rest_framework import generics, permissions, serializers
from .models import FilmmakerApplication
from .serializers import FilmmakerApplicationSerializer

class ApplicationCreateView(generics.CreateAPIView):
    queryset = FilmmakerApplication.objects.all()
    serializer_class = FilmmakerApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Prevent users from submitting more than one application
        if FilmmakerApplication.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError({"detail": "You have already submitted an application."})
        serializer.save(user=self.request.user)
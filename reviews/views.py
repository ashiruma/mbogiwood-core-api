# reviews/views.py
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from films.models import Film
from .permissions import HasPurchasedFilm

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        film_slug = self.kwargs['film_slug']
        return Review.objects.filter(film__slug=film_slug)

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, HasPurchasedFilm]

    def perform_create(self, serializer):
        film_slug = self.kwargs['film_slug']
        film = Film.objects.get(slug=film_slug)
        # Check object-level permission before saving
        self.check_object_permissions(self.request, film)
        serializer.save(user=self.request.user, film=film)
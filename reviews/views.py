# reviews/views.py

from rest_framework import generics, permissions
from films.models import Film
from .models import Review, Rating
from .serializers import ReviewSerializer, RatingSerializer
from .permissions import HasPurchasedFilm


# -------------------------
# Review Views
# -------------------------

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET: List reviews for a film
    POST: Create a new review (must have purchased film)
    """
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), HasPurchasedFilm()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        film_slug = self.kwargs["film_slug"]
        return Review.objects.filter(film__slug=film_slug)

    def perform_create(self, serializer):
        film_slug = self.kwargs["film_slug"]
        film = Film.objects.get(slug=film_slug)
        self.check_object_permissions(self.request, film)  # ensures HasPurchasedFilm works
        serializer.save(user=self.request.user, film=film)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a review
    PUT/PATCH: Update your review
    DELETE: Delete your review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# -------------------------
# Rating Views
# -------------------------

class RatingListCreateView(generics.ListCreateAPIView):
    """
    GET: List ratings for a film
    POST: Create a rating (must have purchased film)
    """
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), HasPurchasedFilm()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        film_slug = self.kwargs["film_slug"]
        return Rating.objects.filter(film__slug=film_slug)

    def perform_create(self, serializer):
        film_slug = self.kwargs["film_slug"]
        film = Film.objects.get(slug=film_slug)
        self.check_object_permissions(self.request, film)
        serializer.save(user=self.request.user, film=film)


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a rating
    PUT/PATCH: Update your rating
    DELETE: Delete your rating
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

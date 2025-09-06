# community/views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Post, Comment, Like, FilmRating
from .serializers import PostSerializer, CommentSerializer, FilmRatingSerializer
from .permissions import IsOwnerOrReadOnly # NEW: Import custom permission

# --- Post Views ---

class PostListCreateView(generics.ListCreateAPIView):
    """
    Lists all posts or creates a new one.
    - GET: Returns a list of all posts.
    - POST: Creates a new post. The author is automatically set to the logged-in user.
    """
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Ensure the author of the post is the logged-in user."""
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific post.
    Only the author of the post can update or delete it.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # UPDATED: Use custom permission to restrict editing/deleting to the author.
    permission_classes = [IsOwnerOrReadOnly]

# --- Comment Views ---

class CommentListCreateView(generics.ListCreateAPIView):
    """
    Lists all comments for a specific post or creates a new comment for it.
    - GET: Returns comments for the post specified in the URL (e.g., /posts/1/comments/).
    - POST: Creates a new comment for that post.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter comments to only those belonging to the specified post."""
        post_pk = self.kwargs['post_pk']
        return Comment.objects.filter(post_id=post_pk)

    def perform_create(self, serializer):
        """Associate the comment with the post from the URL and the logged-in user."""
        # UPDATED: Use get_object_or_404 for a cleaner, safer way to fetch the post.
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)

# NEW: Added a detail view for comments
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific comment.
    Only the author of the comment can update or delete it.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

# --- Like View ---

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request, post_pk):
    """
    Toggles a 'like' on a post for the logged-in user.
    - If the user hasn't liked the post, a 'like' is created.
    - If the user has already liked the post, the 'like' is removed.
    """
    post = get_object_or_404(Post, pk=post_pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        return Response({"detail": "Like removed.", "liked": False}, status=status.HTTP_200_OK)

    return Response({"detail": "Like added.", "liked": True}, status=status.HTTP_201_CREATED)

# --- Film Rating Views ---

class FilmRatingView(generics.ListCreateAPIView):
    """
    - GET: Lists all ratings for a specific film.
    - POST: Creates a new rating or updates an existing one for a film.
    """
    serializer_class = FilmRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter ratings to only those belonging to the specified film."""
        return FilmRating.objects.filter(film_id=self.kwargs['film_pk'])

    def perform_create(self, serializer):
        """
        Creates or updates a rating. This prevents a user from rating the same film multiple times.
        """
        film_id = self.kwargs.get('film_pk')
        # UPDATED: Use update_or_create to prevent duplicate ratings.
        # It finds a rating by the same user for the same film and updates it.
        # If one doesn't exist, it creates it.
        FilmRating.objects.update_or_create(
            user=self.request.user,
            film_id=film_id,
            defaults={'score': serializer.validated_data['score']}
        )
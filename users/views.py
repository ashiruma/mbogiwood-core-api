from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import UserSerializer

User = get_user_model()


class UserListView(APIView):
    """
    List all users (admin only).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    Retrieve a user profile.
    - A user can view their own profile.
    - Admins can view any profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Only allow self or admin
        if request.user != user and not request.user.is_staff:
            return Response({"error": "Forbidden"}, status=403)

        serializer = UserSerializer(user)
        return Response(serializer.data)

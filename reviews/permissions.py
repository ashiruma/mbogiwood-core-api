# reviews/permissions.py
from rest_framework import permissions
from payments.models import Order

class HasPurchasedFilm(permissions.BasePermission):
    message = 'You must purchase this film to leave a review.'

    def has_object_permission(self, request, view, obj):
        # Check if a successful order exists for this user and this film
        return Order.objects.filter(user=request.user, film=obj, status=Order.SUCCESS).exists()
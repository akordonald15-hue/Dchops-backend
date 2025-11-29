from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the review owner can edit/delete.
    Everyone else can only read.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS (read-only requests)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the owner can update/delete
        return obj.user == request.user

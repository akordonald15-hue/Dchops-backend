from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and (user.is_staff or obj.user == user)

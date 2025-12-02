from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
import logging

from .models import MenuItem
from .serializers import MenuItemSerializer

# Logger
admin_logger = logging.getLogger('admin_actions')

# Cache key
CACHE_KEY = "public_menu_list_v1"


class AdminThrottle(UserRateThrottle):
    rate = '50/hour'  # max 50 admin actions per hour


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    ADMIN-ONLY MENU ENDPOINTS
    Create, update, delete menu items.
    Auto-clear public cache after any admin change.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]  # Only admin can modify menu

    # Clear cache on create
    def perform_create(self, serializer):
        item = serializer.save()
        cache.delete(CACHE_KEY)
        admin_logger.info(f"Admin {self.request.user} created menu item {item.id}")
        return item

    # Clear cache on update
    def perform_update(self, serializer):
        item = serializer.save()
        cache.delete(CACHE_KEY)
        admin_logger.info(f"Admin {self.request.user} updated menu item {item.id}")
        return item

    # Clear cache on delete
    def perform_destroy(self, instance):
        admin_logger.info(f"Admin {self.request.user} deleted menu item {instance.id}")
        cache.delete(CACHE_KEY)
        instance.delete()

    # Custom PATCH action: update availability
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAdminUser],
        throttle_classes=[AdminThrottle]
    )
    def update_status(self, request, pk=None):
        item = self.get_object()
        old_status = item.is_available

        new_status = request.data.get('is_available')
        item.is_available = new_status
        item.save()

        # Clear public cache
        cache.delete(CACHE_KEY)

        admin_logger.info(
            f"Admin {request.user.username} updated availability of item {item.id} "
            f"from {old_status} to {new_status}"
        )

        return Response({
            "message": "Status updated",
            "old_status": old_status,
            "new_status": new_status
        })

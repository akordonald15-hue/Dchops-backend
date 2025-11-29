from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAdminUser
from .models import MenuItem
from .serializers import MenuItemSerializer
import logging

# Logger
admin_logger = logging.getLogger('admin_actions')


class AdminThrottle(UserRateThrottle):
    rate = '50/hour'  # max 50 admin actions/hour


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]  # Only admin can modify menu

    # Example admin-only custom action (if needed)
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAdminUser],
        throttle_classes=[AdminThrottle]
    )
    def update_status(self, request, pk=None):
        """
        Example admin action with logging.
        """
        item = self.get_object()
        old_status = item.status

        # Update status from request payload
        new_status = request.data.get('status')
        item.status = new_status
        item.save()

        admin_logger.info(
            f"Admin {request.user.username} updated menu item {item.id} "
            f"from '{old_status}' to '{new_status}'"
        )

        return Response({
            "message": "Status updated",
            "old_status": old_status,
            "new_status": new_status
        })

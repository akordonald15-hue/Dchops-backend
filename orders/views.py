from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import Order
from .serializers import OrderSerializer
import logging

admin_logger = logging.getLogger('admin_actions')


# ----------------------------
#   Permissions
# ----------------------------
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_staff or obj.user == request.user)


# ----------------------------
#   Throttle for Admin
# ----------------------------
class AdminThrottle(UserRateThrottle):
    rate = '50/hour'


# ----------------------------
#   Order ViewSet
# ----------------------------
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Order.objects.all().order_by('-created_at')

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ----------------------------
    #   Admin manually updates status
    # ----------------------------
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAdminUser],
        throttle_classes=[AdminThrottle]
    )
    def update_status(self, request, pk=None):
        order = self.get_object()
        old_status = order.status
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Status field is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        admin_logger.info(
            f"Admin {request.user.username} updated order {order.id} "
            f"status from '{old_status}' to '{new_status}'"
        )

        return Response(
            {'message': f'Order status updated to {new_status}'},
            status=status.HTTP_200_OK
        )

    # ----------------------------
    #   Paystack Webhook
    # ----------------------------
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def paystack_webhook(self, request):
        data = request.data
        reference = data.get('reference')

        if not reference:
            return Response(
                {'error': 'Reference is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # FIXED: correct field name
            order = Order.objects.get(paystack_reference=reference)

            # Update order
            order.paid = True
            order.status = 'PROCESSING'
            order.save()

            return Response(
                {'message': 'Order payment verified and updated.'},
                status=status.HTTP_200_OK
            )

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

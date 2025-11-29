from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

import logging
admin_logger = logging.getLogger('admin_actions')


class AdminThrottle(UserRateThrottle):
    rate = '50/hour'  # Admin can only make 50 admin-status updates per hour


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Automatically assign logged-in user as the review owner.
        """
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[permissions.IsAdminUser],
        throttle_classes=[AdminThrottle]
    )
    def update_status(self, request, pk=None):
        """
        Admin-only: Update review status.
        """
        review = self.get_object()

        old_status = review.status
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Status is required"}, status=400)

        review.status = new_status
        review.save()

        # Log admin action
        admin_logger.info(
            f"Admin {request.user.username} updated review {review.id} "
            f"status from '{old_status}' to '{new_status}'"
        )

        return Response({
            "message": "Review status updated successfully",
            "old_status": old_status,
            "new_status": new_status
        })

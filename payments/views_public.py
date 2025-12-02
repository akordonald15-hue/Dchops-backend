# payments/views_public.py
from django.core.cache import cache
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import permissions
from backend.core.responses import success_response
from .models import PaymentMethod
from .serializers import PaymentMethodSerializer

CACHE_KEY = "public_payment_methods_v1"
CACHE_TTL = 600  # 10 minutes

class PublicPaymentMethodViewSet(ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        cached = cache.get(CACHE_KEY)
        if cached:
            return success_response("Payment methods (cached)", data=cached)

        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        data = serializer.data
        cache.set(CACHE_KEY, data, timeout=CACHE_TTL)
        return success_response("Payment methods fetched", data=data)

from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers
from menu.serializers import MenuItemSerializer
from menu.models import MenuItem

CACHE_KEY = "homepage_v1"
CACHE_TTL = 60

class HomepageSerializer(serializers.Serializer):
    menu = MenuItemSerializer(many=True)

class HomepageAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = HomepageSerializer  # For DRF Spectacular/OpenAPI

    def get(self, request):
        cached = cache.get(CACHE_KEY)
        if cached:
            return Response({
                "success": True,
                "message": "Homepage fetched (cached)",
                "data": cached,
                "errors": None
            })

        menu_items = MenuItemSerializer(MenuItem.objects.filter(is_available=True)[:12], many=True).data
        data = {"menu": menu_items}
        cache.set(CACHE_KEY, data, timeout=CACHE_TTL)
        return Response({
            "success": True,
            "message": "Homepage fetched",
            "data": data,
            "errors": None
        })
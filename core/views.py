from django.core.cache import cache
from rest_framework.views import APIView
from backend.core.responses import success_response
from menu.serializers import MenuItemSerializer
from category.serializers import CategorySerializer
from menu.models import MenuItem
from category.models import Category

CACHE_KEY = "homepage_v1"
CACHE_TTL = 60

class HomepageAPIView(APIView):
    permission_classes = []  # AllowAny

    def get(self, request):
        cached = cache.get(CACHE_KEY)
        if cached:
            return success_response("Homepage fetched (cached)", data=cached)

        categories = CategorySerializer(Category.objects.all(), many=True).data
        menu_items = MenuItemSerializer(MenuItem.objects.filter(is_available=True)[:12], many=True).data
        data = {"categories": categories, "menu": menu_items}
        cache.set(CACHE_KEY, data, timeout=CACHE_TTL)
        return success_response("Homepage fetched", data=data)

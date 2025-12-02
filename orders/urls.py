from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderCreateAPIView

router = DefaultRouter()
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('create/', OrderCreateAPIView.as_view(), name='order-create'),  # ✅ BEFORE router
    path('', include(router.urls)),
]
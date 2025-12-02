from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet
from .public_views import PublicMenuViewSet

admin_router = DefaultRouter()
admin_router.register("items", MenuItemViewSet, basename="admin-menu")

public_router = DefaultRouter()
public_router.register("menu", PublicMenuViewSet, basename="public-menu")

urlpatterns = [
    path("admin/", include(admin_router.urls)),
    path("public/", include(public_router.urls)),
]

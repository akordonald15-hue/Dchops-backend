from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/menu/', include('menu.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/payments/', include('payments.urls')),
]

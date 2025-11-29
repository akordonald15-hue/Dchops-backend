# payments/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('initialize/', views.initialize_payment, name='paystack-initialize'),
    path('verify/', views.verify_payment, name='paystack-verify'),
    path('webhook/', views.paystack_webhook, name='paystack-webhook'),
]

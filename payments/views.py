# payments/views.py

import requests
import hmac, hashlib
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order


# ============================================================
# 1️⃣ INITIALIZE PAYMENT
# ============================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    """
    Initialize a Paystack transaction.
    Frontend sends: { "order_id": <id>, "callback_url": "<url>" }
    """
    order_id = request.data.get("order_id")
    callback_url = request.data.get("callback_url")

    if not order_id:
        return Response({"detail": "order_id is required"}, status=400)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=404)

    if order.paid:
        return Response({"detail": "Order already paid"}, status=400)

    if not order.items.exists() or order.total <= 0:
        return Response({"detail": "Invalid order"}, status=400)

    initialize_url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

    payload = {
        "email": request.user.email,
        "amount": int(order.total * 100),  # convert naira to kobo
        "currency": "NGN",
        "reference": f"order-{order.id}",
        "metadata": {"order_id": order.id},
        "callback_url": callback_url,
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(initialize_url, json=payload, headers=headers)

    if response.status_code not in [200, 201]:
        return Response(
            {"detail": "Paystack init failed", "paystack": response.json()},
            status=502
        )

    paystack_data = response.json()

    # Store reference in DB
    order.paystack_reference = paystack_data["data"]["reference"]
    order.save()

    return Response(paystack_data)



# ============================================================
# 2️⃣ VERIFY PAYMENT (Frontend confirmation)
# ============================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    reference = request.data.get("reference")
    if not reference:
        return Response({"detail": "reference is required"}, status=400)

    verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(verify_url, headers=headers)

    if response.status_code != 200:
        return Response({"detail": "Verification failed"}, status=502)

    result = response.json()
    data = result.get("data", {})

    if data.get("status") != "success":
        return Response({"detail": "Payment not successful"}, status=400)

    # Retrieve order
    order_id = data.get("metadata", {}).get("order_id")

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=404)

    # Mark order as paid
    order.paid = True
    order.save()

    return Response({"detail": "Payment verified", "status": "paid"})


# ============================================================
# 3️⃣ PAYSTACK WEBHOOK (SERVER CONFIRMATION)
# ============================================================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook(request):
    signature = request.headers.get("x-paystack-signature")

    if not signature:
        return Response({"detail": "Missing signature"}, status=400)

    body = request.body
    secret = settings.PAYSTACK_SECRET_KEY.encode()
    expected = hmac.new(secret, body, hashlib.sha512).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return Response({"detail": "Invalid signature"}, status=403)

    event = request.data.get("event")
    data = request.data.get("data", {})

    # Only handle success events
    if event == "charge.success":
        reference = data.get("reference")
        order_id = data.get("metadata", {}).get("order_id")

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.paystack_reference = reference
                order.save()
            except Order.DoesNotExist:
                pass

    return Response({"status": "ok"})

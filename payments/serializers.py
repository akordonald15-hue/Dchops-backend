# payments/serializers.py
from rest_framework import serializers

# ----------------------------
# 1️ Initialize Payment Request
# ----------------------------
class InitializePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    callback_url = serializers.URLField(required=False)


# ----------------------------
# 2️ Verify Payment Request
# ----------------------------
class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField()


# ----------------------------
# 3️ Paystack Webhook
# ----------------------------
class PaystackWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    data = serializers.DictField()


# ----------------------------
# 4️ Initialize Payment Response (from Paystack)
# ----------------------------
class PaymentInitResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()


# ----------------------------
# 5️ Verify Payment Response
# ----------------------------
class PaymentVerifyResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    status = serializers.CharField()

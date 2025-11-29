import hashlib
import hmac
import json
from django.conf import settings
from django.http import HttpResponse
from orders.models import Order

def paystack_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Verify signature
    signature = request.headers.get('X-Paystack-Signature')
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        request.body,
        hashlib.sha512
    ).hexdigest()

    if signature != computed:
        return HttpResponse(status=401)

    payload = json.loads(request.body)
    event = payload.get('event')

    if event == "charge.success":
        reference = payload['data']['reference']

        try:
            order = Order.objects.get(paystack_reference=reference)
            order.paid = True
            order.status = "completed"  # match your Order.STATUS_CHOICES
            order.save()
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)

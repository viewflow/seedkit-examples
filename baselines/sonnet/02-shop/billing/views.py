import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price": request.POST["price_id"],
                "quantity": 1,
            }
        ],
        success_url=request.build_absolute_uri(reverse("pages:index")),
        cancel_url=request.build_absolute_uri(reverse("pages:index")),
    )
    return JsonResponse({"id": session.id, "url": session.url})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponseBadRequest("invalid payload or signature")

    if event["type"] == "checkout.session.completed":
        pass  # fulfil the order

    return HttpResponse(status=200)

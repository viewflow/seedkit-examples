"""Catalogue browsing and Stripe checkout."""

import logging

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from shop import billing
from shop.models import Order, OrderItem, Product

logger = logging.getLogger(__name__)


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class CheckoutSuccessView(TemplateView):
    template_name = "shop/checkout_success.html"


class CheckoutCancelView(TemplateView):
    template_name = "shop/checkout_cancel.html"


@require_POST
def start_checkout(request: HttpRequest, slug: str) -> HttpResponse:
    """Create a one-item order and hand the buyer over to Stripe Checkout."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    email = request.POST.get("email", "").strip()
    if not email and request.user.is_authenticated:
        email = request.user.get_username()
    if not email:
        return HttpResponse("An e-mail address is required.", status=400)

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            total=product.price,
            currency=settings.STRIPE_CURRENCY,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            unit_price=product.price,
            quantity=1,
        )

    session = billing.create_checkout_session(order)
    return HttpResponseRedirect(session.url or product.get_absolute_url())


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Endpoint Stripe posts payment events to."""
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = billing.construct_webhook_event(request.body, signature)
    except (ValueError, RuntimeError, stripe.SignatureVerificationError) as exc:
        logger.warning("Rejected Stripe webhook: %s", exc)
        return HttpResponse(status=400)

    billing.handle_event(event)
    return HttpResponse(status=200)

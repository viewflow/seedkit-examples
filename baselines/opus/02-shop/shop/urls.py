from django.urls import path

from shop import views

app_name = "shop"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product-list"),
    path("checkout/success/", views.CheckoutSuccessView.as_view(), name="checkout-success"),
    path("checkout/cancel/", views.CheckoutCancelView.as_view(), name="checkout-cancel"),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe-webhook"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("<slug:slug>/checkout/", views.start_checkout, name="start-checkout"),
]

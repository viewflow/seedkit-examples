"""Catalogue and order models."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Product(models.Model):
    """Something for sale. Prices are stored in the shop's single currency."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("shop:product-detail", kwargs={"slug": self.slug})

    @property
    def price_cents(self) -> int:
        """Stripe wants the amount in the currency's minor unit."""
        return int(self.price * 100)


class Order(models.Model):
    """A single checkout attempt, paid or otherwise."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    email = models.EmailField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="usd")
    stripe_session_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        # Reverse accessor from OrderItem.order; declared for the type checker only.
        items: models.Manager["OrderItem"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.reference} ({self.status})"

    def recalculate_total(self) -> Decimal:
        total = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        self.total = total
        return total


class OrderItem(models.Model):
    """A line on an order. Name and price are snapshotted at purchase time."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name="+")
    name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.quantity} x {self.name}"

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

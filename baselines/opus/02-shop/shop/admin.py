from django.contrib import admin

from shop.models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "is_active", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal"]

    @admin.display(description="Subtotal")
    def subtotal(self, obj: OrderItem) -> str:
        return f"{obj.subtotal:.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "email", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["reference", "email", "stripe_session_id"]
    readonly_fields = ["reference", "stripe_session_id", "stripe_payment_intent", "created_at"]
    inlines = [OrderItemInline]

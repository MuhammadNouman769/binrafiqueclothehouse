from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.utils.models import BaseModel
from apps.products.models.product_variant import ProductVariant


class Order(BaseModel):
    """
    Order placed by a guest user.
    """
    session_key = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Session key of the guest user"
    )

    # Customer Details
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)

    # Order Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Order ID (Auto-generated like BR-20260812-ABCD)
    order_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
    )

    class Meta:
        db_table = "orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a unique order ID: BR-YYYYMMDD-Random4
            date_str = timezone.now().strftime("%Y%m%d")
            rand_str = get_random_string(4).upper()
            self.order_id = f"BR-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    @property
    def whatsapp_message(self):
        """Generate a WhatsApp friendly order summary (Plain Text)"""
        msg = f"NEW ORDER: {self.order_id}\n"
        msg += f"Name: {self.full_name}\n"
        msg += f"Phone: {self.phone}\n"
        msg += f"Address: {self.address}, {self.city}\n\n"
        msg += "ITEMS:\n"
        for item in self.items.all():
            msg += f"- {item.variant.product.name} ({item.variant.variant_name}) x {item.quantity} = PKR {item.total_price}\n"
        msg += f"\nTOTAL: PKR {self.total_amount}\n"
        msg += "Payment: Cash on Delivery"
        return msg

    def __str__(self):
        return f"Order {self.order_id} - {self.full_name}"


class OrderItem(BaseModel):
    """
    Individual item inside an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,  #  Prevents deletion if ordered
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price at the time of checkout (to preserve historical price)"
    )

    class Meta:
        db_table = "order_items"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name}"
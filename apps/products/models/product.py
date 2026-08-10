from django.db import models

from apps.utils.models import SlugModel
from apps.products.models.product_category import ProductCategory


"""
===============================================================================
                                PRODUCT
===============================================================================
"""


class Product(SlugModel):

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
    )

    name = models.CharField(
        max_length=255,
        db_index=True,
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    trending = models.BooleanField(
        default=False,
    )

    is_new_arrival = models.BooleanField(
        default=False,
        help_text="Check this to show product in New Arrivals section",
    )

    is_bestseller = models.BooleanField(
        default=False,
        help_text="Check this to show product in Bestseller section",
    )

    class Meta:
        db_table = "products"

        verbose_name = "Product"
        verbose_name_plural = "Products"

        ordering = (
            "name",
        )

        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["name"]),
            models.Index(fields=["trending"]),            # ✅ Fixed: is_featured → trending
            models.Index(fields=["is_new_arrival"]),      # ✅ Added for speed
            models.Index(fields=["is_bestseller"]),       # ✅ Added for speed
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    # ------------------------------------------------------------------
    # Variant Helpers
    # ------------------------------------------------------------------

    @property
    def has_variants(self):
        return self.variants.filter(is_active=True).exists()

    @property
    def default_variant(self):
        return (
            self.variants.filter(
                is_default=True,
                is_active=True,
            ).first()
            or self.variants.filter(
                is_active=True,
            ).first()
        )

    # ------------------------------------------------------------------
    # Main Image
    # ------------------------------------------------------------------

    @property
    def main_image(self):
        variant = self.default_variant

        if not variant:
            return None

        return variant.primary_image

    # ------------------------------------------------------------------
    # String
    # ------------------------------------------------------------------

    def __str__(self):
        return self.name
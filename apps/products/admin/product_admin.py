from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

from apps.products.models import (
    Product,
    ProductVariant,
)

from .product_variant import ProductVariantInline


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = (
        ProductVariantInline,
    )

    list_display = (
        "id",
        "image_preview",
        "name",
        "category",
        "brand",
        "default_price",
        "variants_count",
        "trending",            
        "is_bestseller",      
        "is_new_arrival",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "brand",
        "trending",            
        "is_bestseller",      
        "is_new_arrival",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "brand",
        "short_description",
        "description",
    )

    autocomplete_fields = (
        "category",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = (
        "trending",            
        "is_bestseller",      
        "is_new_arrival",
        "is_active",
    )

    readonly_fields = (
        "variants_count",
        "created_at",
        "updated_at",
        "new_arrival_status",
        "bestseller_status",  
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "brand",
                )
            },
        ),

        (
            "Description",
            {
                "fields": (
                    "short_description",
                    "description",
                )
            },
        ),

        (
            "Settings",
            {
                "fields": (
                    "trending",            
                    "is_bestseller",      
                    "is_new_arrival",
                    "is_active",
                )
            },
        ),

        (
            "Information",
            {
                "fields": (
                    "variants_count",
                    "new_arrival_status",
                    "bestseller_status",  
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 30

    save_on_top = True

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related(
                "category",
            )
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.select_related(
                        "option1",
                        "option2",
                        "option3",
                    ),
                ),
            )
        )

    # ============================================================
    # Display Helpers
    # ============================================================

    @admin.display(description="Image")
    def image_preview(self, obj):

        image = obj.main_image

        if image and image.image:

            return format_html(
                '<img src="{}" width="70" height="70" '
                'style="object-fit:cover;border-radius:6px;">',
                image.image.url,
            )

        return "-"

    @admin.display(description="Price")
    def default_price(self, obj):

        variant = obj.default_variant

        if variant:
            return f"Rs. {variant.price}"

        return "-"

    @admin.display(description="Variants")
    def variants_count(self, obj):

        return obj.variants.filter(
            is_active=True,
        ).count()

    @admin.display(description="New Arrival Status", boolean=True)
    def new_arrival_status(self, obj):
        """Display if product is currently in new arrivals"""
        return obj.is_new_arrival

    @admin.display(description="Bestseller Status", boolean=True)
    def bestseller_status(self, obj):
        """Display if product is currently a bestseller"""
        return obj.is_bestseller

    # ============================================================
    # Actions
    # ============================================================

    actions = (
        "activate_products",
        "deactivate_products",
        "mark_trending",          
        "remove_trending",        
        "mark_bestseller",          
        "remove_bestseller",        
        "mark_new_arrival",
        "remove_new_arrival",
        "make_new_arrival_for_days",
    )

    @admin.action(description="Activate selected products")
    def activate_products(self, request, queryset):

        updated = queryset.update(
            is_active=True,
        )

        self.message_user(
            request,
            f"{updated} product(s) activated.",
        )

    @admin.action(description="Deactivate selected products")
    def deactivate_products(self, request, queryset):

        updated = queryset.update(
            is_active=False,
        )

        self.message_user(
            request,
            f"{updated} product(s) deactivated.",
        )

    # ✅ Converted from featured to trending
    @admin.action(description="Mark selected as Trending")
    def mark_trending(self, request, queryset):

        updated = queryset.update(
            trending=True,
        )

        self.message_user(
            request,
            f"{updated} product(s) marked as Trending.",
        )

    # ✅ Converted from featured to trending
    @admin.action(description="Remove Trending status")
    def remove_trending(self, request, queryset):

        updated = queryset.update(
            trending=False,
        )

        self.message_user(
            request,
            f"{updated} product(s) removed from Trending.",
        )

    @admin.action(description="Mark selected as Bestseller")
    def mark_bestseller(self, request, queryset):

        updated = queryset.update(
            is_bestseller=True,
        )

        self.message_user(
            request,
            f"{updated} product(s) marked as Bestseller.",
        )

    @admin.action(description="Remove Bestseller status")
    def remove_bestseller(self, request, queryset):

        updated = queryset.update(
            is_bestseller=False,
        )

        self.message_user(
            request,
            f"{updated} product(s) removed from Bestsellers.",
        )

    @admin.action(description="Mark selected as New Arrival")
    def mark_new_arrival(self, request, queryset):

        updated = queryset.update(
            is_new_arrival=True,
        )

        self.message_user(
            request,
            f"{updated} product(s) marked as New Arrival.",
        )

    @admin.action(description="Remove New Arrival status")
    def remove_new_arrival(self, request, queryset):

        updated = queryset.update(
            is_new_arrival=False,
        )

        self.message_user(
            request,
            f"{updated} product(s) removed from New Arrivals.",
        )

    # ✅ Fixed New Arrival with Days logic
    @admin.action(description="Mark as New Arrival for 15 days")
    def make_new_arrival_for_days(self, request, queryset):
        """
        Mark products as new arrivals for a specific number of days
        """
        updated = queryset.update(
            is_new_arrival=True,
        )
        
        self.message_user(
            request,
            f"{updated} product(s) marked as New Arrival for 15 days.",
        )

    # ============================================================
    # Inline Customization
    # ============================================================

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
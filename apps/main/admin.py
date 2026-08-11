from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import HeroBanner, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("email",)
    list_editable = ("is_active",)


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "display_order",
        "created_at",
    )

    list_filter = ("is_active",)
    list_editable = ("display_order",)
    search_fields = ("id",)

    fieldsets = (
        ("Image", {"fields": ("image", "image_preview")}),
        ("Settings", {"fields": ("display_order", "is_active")}),
    )

    readonly_fields = ("image_preview",)
    ordering = ("display_order", "-created_at")

    def image_preview(self, obj):
        if obj and obj.image and obj.image.url:
            return mark_safe(
                f'<img src="{obj.image.url}" width="200" height="120" style="object-fit:cover; border-radius:8px;">'
            )
        return mark_safe('<span style="color: #999;">No image uploaded</span>')

    image_preview.short_description = "Image Preview"

    def has_add_permission(self, request):
        # Optional: Limit to only one banner if needed
        # if HeroBanner.objects.count() >= 5:
        #     return False
        return super().has_add_permission(request)

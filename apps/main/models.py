from django.db import models

from apps.utils.models import BaseModel


class NewsletterSubscriber(BaseModel):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class HeroBanner(BaseModel):
    """
    Simple Hero Banner - Only Image
    """

    image = models.ImageField(
        upload_to="hero_banners/", help_text="Banner image (recommended: 1920x800)"
    )

    display_order = models.PositiveSmallIntegerField(
        default=0, help_text="Lower number = higher priority"
    )

    class Meta:
        db_table = "hero_banners"
        verbose_name = "Hero Banner"
        verbose_name_plural = "Hero Banners"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"Banner {self.id}"

    def image_preview(self):
        if self.image:
            return f'<img src="{self.image.url}" width="100" height="50" style="object-fit:cover;" />'
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = "Image Preview"

from django.db.models import Prefetch

from apps.products.models.product_category import ProductCategory


def menu_categories(request):
    """
    Context processor to add menu categories to all templates.
    """
    categories = (
        ProductCategory.objects.filter(
            parent__isnull=True,
            is_active=True,
        )
        .prefetch_related(
            Prefetch(
                "children",
                queryset=ProductCategory.objects.filter(is_active=True).order_by(
                    "display_order", "title"
                ),
            )
        )
        .order_by("display_order", "title")
    )

    #  FIX: Rename 'menu_categories' to 'header_categories' to avoid conflict
    return {
        "header_categories": categories,
    }

from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, TemplateView

from apps.main.models import HeroBanner
from apps.products.models.product import Product
from apps.products.models.product_category import ProductCategory
from apps.products.models.product_variant import ProductVariant
from apps.products.models.variant_image import VariantImage
from apps.testimonials.models.testimonial import Testimonial


""" ========================= Home View ========================= """
class HomeView(TemplateView):
    template_name = "pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ------------------------------------------------------
        # Variant & Product Queries
        # ------------------------------------------------------

        variant_queryset = (
            ProductVariant.objects.filter(is_active=True)
            .select_related("option1", "option2", "option3")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=VariantImage.objects.filter(is_active=True).order_by(
                        "-is_primary", "position", "id"
                    ),
                ),
            )
            .order_by("-is_default", "position", "id")
        )

        product_queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                Prefetch("variants", queryset=variant_queryset),
            )
        )

        # ------------------------------------------------------
        # Parent Categories (for header tabs)
        # ------------------------------------------------------
        parent_categories = (
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

        featured_parent_categories = parent_categories[:4]

        context["parent_categories"] = featured_parent_categories

        # ======================================================
        # 1. TRENDING PRODUCTS
        # ======================================================
        context["trending_products"] = product_queryset.filter(trending=True).order_by(
            "-created_at"
        )[:8]

        # ======================================================
        # 2. CATEGORY WISE PRODUCTS (for tabs)
        # ======================================================
        category_products_list = []
        for category in featured_parent_categories:
            category_ids = [category.id]
            category_ids.extend(
                category.children.filter(is_active=True).values_list("id", flat=True)
            )
            products = (
                product_queryset.filter(category_id__in=category_ids)
                .distinct()
                .order_by("-created_at")[:8]
            )
            category_products_list.append(
                {
                    "category": category,
                    "products": products,
                }
            )
        context["category_products_list"] = category_products_list

        # ======================================================
        # 3. NEW ARRIVALS (DUAL LOGIC FOR DEBUGGING)
        # ======================================================

        # 3a. Strictly marked as New Arrival
        new_arrivals_strict = list(
            product_queryset.filter(is_new_arrival=True).order_by("-created_at")
        )

        # 3b. Fallback (Latest 8 products if strict count is low)
        new_arrivals_fallback = list(product_queryset.order_by("-created_at")[:8])

        if new_arrivals_strict:
            context["new_arrivals"] = new_arrivals_strict[:8]
            print(
                f" DEBUG: Found {len(new_arrivals_strict)} New Arrival products!"
            )  # Check terminal
        else:
            context["new_arrivals"] = new_arrivals_fallback
            print(
                f" DEBUG: No 'is_new_arrival' products found. Showing {len(new_arrivals_fallback)} Latest products instead."
            )  # Check terminal

        # ======================================================
        # 4. BESTSELLER PRODUCTS
        # ======================================================
        bestseller_products = list(
            product_queryset.filter(is_bestseller=True).order_by("-created_at")[:6]
        )

        if len(bestseller_products) < 6:
            needed = 6 - len(bestseller_products)
            additional = (
                product_queryset.filter(trending=True)
                .exclude(id__in=[p.id for p in bestseller_products])
                .order_by("-created_at")[:needed]
            )
            bestseller_products.extend(additional)

        if len(bestseller_products) < 6:
            needed = 6 - len(bestseller_products)
            additional = product_queryset.exclude(
                id__in=[p.id for p in bestseller_products]
            ).order_by("-created_at")[:needed]
            bestseller_products.extend(additional)

        context["bestseller_products"] = bestseller_products
        context["bestseller_remaining"] = product_queryset.exclude(
            id__in=[p.id for p in bestseller_products]
        ).order_by("-created_at")[:4]

        # ======================================================
        # 5. TESTIMONIALS & BANNERS
        # ======================================================
        context["testimonials"] = Testimonial.objects.filter(is_active=True).order_by(
            "display_order", "-created_at"
        )[:10]

        context["hero_banners"] = HeroBanner.objects.filter(is_active=True).order_by(
            "display_order", "-created_at"
        )

        return context


""" ========================= Product List View ========================= """
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        variant_queryset = (
            ProductVariant.objects.filter(is_active=True)
            .select_related("option1", "option2", "option3")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=VariantImage.objects.filter(is_active=True).order_by(
                        "-is_primary", "position", "id"
                    ),
                ),
            )
            .order_by("-is_default", "position", "id")
        )

        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                Prefetch("variants", queryset=variant_queryset),
            )
        )

        #  FIX: Category Filter (Handles both Slug and Title)
        category_param = self.request.GET.get("category")
        if category_param:
            try:
                category = ProductCategory.objects.get(
                    Q(slug=category_param) | Q(title__iexact=category_param),
                    is_active=True,
                )
                category_ids = [category.id]
                category_ids.extend(
                    category.children.filter(is_active=True).values_list(
                        "id", flat=True
                    )
                )
                queryset = queryset.filter(category_id__in=category_ids)
            except ProductCategory.DoesNotExist:
                pass

        # Search
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(brand__icontains=search_query)
                | Q(short_description__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # Sorting
        sort = self.request.GET.get("sort")
        if sort == "price_low":
            queryset = queryset.order_by("variants__price")
        elif sort == "price_high":
            queryset = queryset.order_by("-variants__price")
        elif sort == "name_asc":
            queryset = queryset.order_by("name")
        elif sort == "name_desc":
            queryset = queryset.order_by("-name")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["sort_by"] = self.request.GET.get("sort", "")
        context["category_slug"] = self.request.GET.get("category", "")
        return context


""" ========================= Product Detail View ========================= """
class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(is_active=True)
                    .select_related(
                        "option1__option", "option2__option", "option3__option"
                    )
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=VariantImage.objects.filter(
                                is_active=True
                            ).order_by("-is_primary", "position", "id"),
                        )
                    )
                    .order_by("-is_default", "position", "id"),
                )
            ),
            slug=slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        variants = product.variants.filter(is_active=True)

        # Default Variant
        default_variant = variants.filter(is_default=True).first()
        if not default_variant:
            default_variant = variants.first()

        default_image = None
        if default_variant:
            default_image = default_variant.images.filter(is_active=True).first()

        # Related Products
        related_products = (
            Product.objects.filter(category=product.category, is_active=True)
            .exclude(pk=product.pk)
            .prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True
                    ).prefetch_related(
                        Prefetch(
                            "images",
                            queryset=VariantImage.objects.filter(
                                is_active=True
                            ).order_by("-is_primary", "position", "id"),
                        )
                    ),
                )
            )
            .order_by("-created_at")[:8]
        )

        context["default_variant"] = default_variant
        context["default_image"] = default_image
        context["related_products"] = related_products

        return context


""" ========================= AJAX Search Suggestions View ========================="""
@require_GET
def search_suggestions(request):
    """
    AJAX endpoint for live search suggestions.
    """
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    suggestions = []
    seen = set()

    # ==========================================
    # 1. Search Products
    # ==========================================
    products = Product.objects.filter(
        Q(name__icontains=query)
        | Q(brand__icontains=query)
        | Q(short_description__icontains=query),
        is_active=True,
    ).select_related("category")[:8]

    for product in products:
        if product.name not in seen:
            seen.add(product.name)
            suggestions.append(
                {
                    "name": product.name,
                    "category": (
                        product.category.title if product.category else "Product"
                    ),
                    "type": "Product",
                    "icon": "fas fa-box",
                    "url": (
                        product.get_absolute_url()
                        if hasattr(product, "get_absolute_url")
                        else None
                    ),
                }
            )

    # ==========================================
    # 2. Search Categories
    # ==========================================
    categories = ProductCategory.objects.filter(
        Q(title__icontains=query), is_active=True
    )[:5]

    for category in categories:
        if category.title not in seen:
            seen.add(category.title)
            suggestions.append(
                {
                    "name": category.title,
                    "category": "Category",
                    "type": "Category",
                    "icon": "fas fa-tag",
                    "url": f"/products/?category={category.slug}",
                }
            )

    # ==========================================
    # 3. Search Brands
    # ==========================================
    brands = (
        Product.objects.filter(brand__icontains=query, is_active=True)
        .exclude(brand__isnull=True)
        .exclude(brand__exact="")
        .values_list("brand", flat=True)
        .distinct()[:3]
    )

    for brand in brands:
        if brand and brand not in seen:
            seen.add(brand)
            suggestions.append(
                {
                    "name": brand,
                    "category": "Brand",
                    "type": "Brand",
                    "icon": "fas fa-building",
                    "url": f"/products/?q={brand}",
                }
            )

    return JsonResponse({"suggestions": suggestions[:15]})

from django.urls import path

from apps.products.views import (
    HomeView,
    ProductDetailView,
    ProductListView,
    search_suggestions,
)

app_name = "products"

urlpatterns = [
    path("", HomeView.as_view(), name="home-view"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("search-suggestions/", search_suggestions, name="search_suggestions"),
]

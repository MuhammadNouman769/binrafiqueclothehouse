from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import serve_media

urlpatterns = [
    path("nested_admin/", include("nested_admin.urls")),
    path("admin/", admin.site.urls),
    
    path("", include("apps.products.urls")),
    path("", include("apps.main.urls")),
    path("", include("apps.contact.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("media/<path:path>/", serve_media, name="serve_media"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
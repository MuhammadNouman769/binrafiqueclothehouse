from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import serve_media

urlpatterns = [
    path("nested_admin/", include("nested_admin.urls")),
    path("admin/", admin.site.urls),
    
    # ============================================
    # Project Apps
    # ============================================
    path("", include("apps.products.urls")),
    path("", include("apps.main.urls")),
    path("", include("apps.contact.urls")),
    
    #  Newly Added Cart & Orders
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    
    # ============================================
    # Media serving (Custom View)
    # ============================================
    path("media/<path:path>/", serve_media, name="serve_media"),
]

# ============================================
# MEDIA & STATIC FILES SERVING (Development)
# ============================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ============================================================
# ERROR HANDLERS
# ============================================================
handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
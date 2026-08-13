from pathlib import Path
from decouple import config

# ============================================
# BASE DIRECTORY
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY
# ============================================

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# ============================================
# EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# ============================================
# INSTALLED APPS
# ============================================

INSTALLED_APPS = [
    "unfold",                     # ✅ Sab se upar
    
    # Django Default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party
    "nested_admin",
    "whitenoise.runserver_nostatic",

    # Local Apps
    "apps.utils",
    "apps.main",
    "apps.products",
    "apps.cart",
    "apps.orders",
    "apps.whatspp",
    "apps.contact",
    "apps.testimonials",
]

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================
# URL CONFIGURATION
# ============================================

ROOT_URLCONF = "core.urls"

# ============================================
# TEMPLATES
# ============================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.products.context_processors.menu_categories",
                "apps.whatspp.context_processors.site_settings",
            ],
        },
    },
]

# ============================================
# WSGI / DATABASE / PASSWORD
# ============================================

WSGI_APPLICATION = "core.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC & MEDIA
# ============================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    WHITENOISE_USE_FINDERS = True
    STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "media"]

# ==========================================================
# ✅ UNFOLD CONFIGURATION - FINAL WORKING VERSION
# ==========================================================

from django.templatetags.static import static

UNFOLD = {
    "SITE_TITLE": "Tahir Rafique Clothe House Admin",
    "SITE_HEADER": "Tahir Rafique Clothe House",
    "SITE_LOGO": lambda request: static("logos/logo-.png"),
    "STYLES": [
        lambda request: static("css/admin-custom.css"),
    ],
    "COLORS": {
        "primary": {
            "50": "#f0f9ff",
            "100": "#e0f2fe",
            "200": "#bae6fd",
            "300": "#7dd3fc",
            "400": "#38bdf8",
            "500": "#0ea5e9",
            "600": "#0284c7",
            "700": "#0369a1",
            "800": "#075985",
            "900": "#0c4a6e",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "items": [{"title": "Dashboard", "icon": "dashboard", "link": "/admin/"}],
            },
            {
                "title": "Products",
                "separator": True,
                "items": [
                    {"title": "Products", "icon": "inventory_2", "link": "/admin/products/product/"},
                    {"title": "Categories", "icon": "category", "link": "/admin/products/productcategory/"},
                    {"title": "Variants", "icon": "cached", "link": "/admin/products/productvariant/"},
                ],
            },
            {
                "title": "Orders",
                "separator": True,
                "items": [{"title": "Orders", "icon": "shopping_cart", "link": "/admin/orders/order/"}],
            },
        ],
    },
}
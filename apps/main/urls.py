from django.urls import path

from .views import (
    FAQsView,
    PrivacyPolicyView,
    SitemapView,
    TermsOfUseView,
    newsletter_subscribe,
)

app_name = "main"

urlpatterns = [
    path("terms-of-use/", TermsOfUseView.as_view(), name="terms-of-use"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("faqs/", FAQsView.as_view(), name="faqs"),
    path("sitemap/", SitemapView.as_view(), name="sitemap"),
    path(
        "newsletter-subscribe/", view=newsletter_subscribe, name="newsletter_subscribe"
    ),
]

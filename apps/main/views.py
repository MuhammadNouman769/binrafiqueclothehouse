from django.views.generic import TemplateView
from django.shortcuts import render
from django.templatetags.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber
from apps.main.models import HeroBanner






@csrf_exempt
@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    
    if NewsletterSubscriber.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'Already subscribed!'})
    
    subscriber = NewsletterSubscriber.objects.create(email=email)
    return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})





class TermsOfUseView(TemplateView):
    template_name = "pages/terms-of-use.html"

class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy-policy.html"

class FAQsView(TemplateView):
    template_name = "pages/faqs.html"

class CartView(TemplateView):
    template_name = "cart/cart.html"    

class CheckoutView(TemplateView):
    template_name = "orders/checkout.html"

class TestimonialView(TemplateView):
    template_name = "testimonials/testimonial.html"

class ErrorView(TemplateView):
    template_name = "errors/404.html"   

class Error500View(TemplateView):
    template_name = "errors/500.html"






class SitemapView(TemplateView):
    template_name = "pages/sitemap.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define sitemap structure - Updated for Tahir Rafique Clothe House
        context['sitemap_sections'] = [
            {
                'title': 'Main Pages',
                'icon': 'fa-home',
                'links': [
                    {'name': 'Home', 'url': 'products:home-view'},
                    {'name': 'Products', 'url': 'products:product-list'},
                    {'name': 'Contact Us', 'url': 'contact:contact'},
                    {'name': 'FAQ', 'url': 'main:faqs'},
                ]
            },
            {
                'title': 'Product Categories',
                'icon': 'fa-tshirt',
                'links': [
                    {'name': 'Shalwar Kameez', 'url': 'products:product-list', 'params': '?category=shalwar-kameez'},
                    {'name': 'Formal Wear', 'url': 'products:product-list', 'params': '?category=formal-wear'},
                    {'name': 'Casual Wear', 'url': 'products:product-list', 'params': '?category=casual-wear'},
                    {'name': 'Semi-Formal', 'url': 'products:product-list', 'params': '?category=semi-formal'},
                    {'name': 'Kurta', 'url': 'products:product-list', 'params': '?category=kurta'},
                    {'name': 'Waistcoats', 'url': 'products:product-list', 'params': '?category=waistcoats'},
                    {'name': 'Sherwani', 'url': 'products:product-list', 'params': '?category=sherwani'},
                    {'name': 'Premium Collection', 'url': 'products:product-list', 'params': '?category=premium'},
                    {'name': 'Eid Collection', 'url': 'products:product-list', 'params': '?category=eid-collection'},
                    {'name': 'Wedding Collection', 'url': 'products:product-list', 'params': '?category=wedding'},
                ]
            },
            {
                'title': 'Fabrics',
                'icon': 'fa-layer-group',
                'links': [
                    {'name': 'Cotton', 'url': 'products:product-list', 'params': '?fabric=cotton'},
                    {'name': 'Lawn', 'url': 'products:product-list', 'params': '?fabric=lawn'},
                    {'name': 'Khadar', 'url': 'products:product-list', 'params': '?fabric=khadar'},
                    {'name': 'Linen', 'url': 'products:product-list', 'params': '?fabric=linen'},
                    {'name': 'Silk', 'url': 'products:product-list', 'params': '?fabric=silk'},
                    {'name': 'Wool', 'url': 'products:product-list', 'params': '?fabric=wool'},
                    {'name': 'Velvet', 'url': 'products:product-list', 'params': '?fabric=velvet'},
                ]
            },
            {
                'title': 'Collections',
                'icon': 'fa-star',
                'links': [
                    {'name': 'Summer Collection', 'url': 'products:product-list', 'params': '?collection=summer'},
                    {'name': 'Winter Collection', 'url': 'products:product-list', 'params': '?collection=winter'},
                    {'name': 'Eid Collection', 'url': 'products:product-list', 'params': '?collection=eid'},
                    {'name': 'Wedding Collection', 'url': 'products:product-list', 'params': '?collection=wedding'},
                    {'name': 'Festive Collection', 'url': 'products:product-list', 'params': '?collection=festive'},
                    {'name': 'New Arrivals', 'url': 'products:product-list', 'params': '?sort=newest'},
                    {'name': 'Best Sellers', 'url': 'products:product-list', 'params': '?sort=popular'},
                ]
            },
            {
                'title': 'Legal Pages',
                'icon': 'fa-gavel',
                'links': [
                    {'name': 'Privacy Policy', 'url': 'main:privacy-policy'},
                    {'name': 'Terms of Use', 'url': 'main:terms-of-use'},
                    {'name': 'Sitemap', 'url': 'main:sitemap'},
                ]
            },
        ]
        
        return context
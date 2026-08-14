from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from urllib.parse import quote
from decimal import Decimal

from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart
from apps.products.models.product_variant import ProductVariant
from apps.whatspp.models.whatsapp_setting import SiteSetting
from .utils import render_to_pdf


class CheckoutView(View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()
        
        if not cart or cart.items.count() == 0:
            messages.warning(request, "Your cart is empty.")
            return redirect('cart:view')

        cart_items = cart.items.all().select_related('variant__product')

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': cart.total_price,
            'total_amount': cart.total_price,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()
        if not cart or cart.items.count() == 0:
            messages.error(request, "Cart is empty.")
            return redirect('products:product-list')

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')

        # Create Order
        order = Order.objects.create(
            session_key=request.session.session_key,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            subtotal=cart.total_price,
            total_amount=cart.total_price,
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.variant.price,
            )

        cart.is_active = False
        cart.save()

        #  Generate PDF Link
        pdf_url = request.build_absolute_uri(reverse('orders:order_pdf', args=[order.order_id]))

        # Get WhatsApp number from SiteSettings
        site_settings = SiteSetting.get_settings()
        whatsapp_number = site_settings.whatsapp_number

        #  Generate WhatsApp Message (Text + PDF Link)
        message = order.whatsapp_message
        message += f"\n\n📄 Download Receipt: {pdf_url}"

        encoded_msg = quote(message)
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_msg}"

        return redirect(whatsapp_url)


#  PDF Download View (For Receipt)
class OrderPDFView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        pdf = render_to_pdf('orders/order_pdf.html', {'order': order})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"Order_{order.order_id}.pdf"
            content = f"inline; filename={filename}"
            response['Content-Disposition'] = content
            return response
        return HttpResponse("PDF generation error")
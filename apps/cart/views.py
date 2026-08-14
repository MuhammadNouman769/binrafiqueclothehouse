from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse

from .models import Cart, CartItem
from apps.products.models.product_variant import ProductVariant

""" =================== CartView =================== """
class CartView(View):
    """Display the current user's cart"""
    template_name = "cart/cart.html"

    def get(self, request):
        cart = self.get_or_create_cart(request)
        
        #  Fetch related products to show in "You May Also Like"
        related_products = []
        if cart.items.exists():
            first_item = cart.items.first()
            if first_item and first_item.variant.product.category:
                related_products = first_item.variant.product.category.products.filter(
                    is_active=True
                ).exclude(
                    id__in=[item.variant.product.id for item in cart.items.all()]
                )[:5]
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all().select_related('variant__product'),
            'related_products': related_products,
        }
        return render(request, self.template_name, context)

    def get_or_create_cart(self, request):
        # FIX: Ensure session key exists before creating cart
        if not request.session.session_key:
            request.session.save()  # This forces a new session key
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


""" ==================== CartItemViw =================== """
class AddToCartView(View):
    """Add a variant to the cart (handles quantity from POST)"""
    def post(self, request, variant_id):
        cart = self.get_or_create_cart(request)
        variant = get_object_or_404(ProductVariant, id=variant_id, is_active=True)

        #  GET QUANTITY FROM FORM (Sent from product detail page)
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        
        if not created:
            # If item already exists, just add the quantity
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # New item, set the exact quantity
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, f"{variant.product.name} added to cart!")
        return redirect('cart:view')

    def get_or_create_cart(self, request):
        #  FIX: Ensure session key exists before creating cart
        if not request.session.session_key:
            request.session.save()  # This forces a new session key
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


""" =================== UpdateCartView ================ """
class UpdateCartView(View):
    """Increase, decrease, or remove items from cart with AJAX"""
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()

        #  Check if it's an AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity if cart_item.pk else 0,
                'item_total': float(cart_item.total_price) if cart_item.pk else 0,
                'cart_total': float(cart.total_price),
                'total_items': cart.total_items,  #  This will be caught by header
            })

        # Fallback for non-AJAX (just in case)
        return redirect('cart:view')

""" ================= GEtCountViw ================ """
class GetCartCountView(View):
    """AJAX endpoint to return total items in cart"""
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'total_items': 0})
        
        cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
        if not cart:
            return JsonResponse({'total_items': 0})
        
        return JsonResponse({'total_items': cart.total_items})    
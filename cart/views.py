from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem

def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, f"Product with ID {product_id} does not exist.")
        return redirect('products:products')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Get or create cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
                    request.session['cart_id'] = cart.id
            else:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        
        # Check for variants
        variant_data = {}
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'product_id', 'quantity'] and value:
                variant_data[key] = value
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # If item already exists, update quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Save variant data if any
        if variant_data:
            cart_item.variant_data = variant_data
            cart_item.save()
        
        messages.success(request, f"{product.name} added to your cart.")
        
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Alternative view function to display the cart contents.
    This is an alias for the cart view.
    """
    return cart(request)

def cart(request):
    """
    View function to display the cart contents.
    """
    # Get the cart
    if request.user.is_authenticated:
        # If user is logged in, get their cart
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, get cart from session
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    # Get cart items
    cart_items = cart.items.all()
    
    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    tax = subtotal * 0.1  # Assuming 10% tax
    shipping = 10.00 if subtotal > 0 else 0.00  # Flat shipping rate
    total = subtotal + tax + shipping
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    
    return render(request, 'cart/cart.html', context)

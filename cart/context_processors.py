from .models import Cart

def cart(request):
    """
    Context processor that provides cart information to all templates.
    Returns the number of items in the cart.
    """
    cart_count = 0
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.item_count if hasattr(cart, 'item_count') else 0
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart_count = cart.item_count if hasattr(cart, 'item_count') else 0
            except Cart.DoesNotExist:
                pass
    
    return {'cart_count': cart_count} 
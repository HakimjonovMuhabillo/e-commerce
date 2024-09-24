from .models import Cart


def cart_context(request):
    cart_total_price = 0
    cart_total_quantity = 0

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_total_price = cart.get_cart_total_price
        cart_total_quantity = cart.get_cart_total_quantity

    return {
        'cart_total_price': cart_total_price,
        'cart_total_quantity': cart_total_quantity,
    }

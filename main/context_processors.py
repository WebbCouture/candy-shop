def cart_item_count(request):
    cart = request.session.get('cart', {})
    if isinstance(cart, dict):
        count = sum(cart.values())  # total quantity of items in dict
    elif isinstance(cart, list):
        count = len(cart)  # if cart is a list, count its length
    else:
        count = 0  # fallback if cart is neither dict nor list
    return {'cart_item_count': count}

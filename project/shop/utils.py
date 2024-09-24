from .models import Product, Cart, CartProduct, Coupon


class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None, color=None, size=None, quantity=1):
        self.user = request.user

        if product_id and action:
            self.add_or_delete(product_id, action, color, size, quantity)

    def get_cart_info(self):
        cart, created = Cart.objects.get_or_create(user=self.user)
        cart_products = cart.cartproduct_set.all()

        cart_total_price = cart.get_cart_total_price
        cart_total_quantity = cart.get_cart_total_quantity

        return {
            'cart': cart,
            'products': cart_products,
            'cart_total_price': cart_total_price,
            'cart_total_quantity': cart_total_quantity
        }

    def add_or_delete(self, product_id, action, color, size, quantity):
        cart = self.get_cart_info()['cart']
        product = Product.objects.get(pk=product_id)
        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product,
                                                                  size=size, color=color)
        if action == 'add' and product.in_stock > quantity:
            cart_product.quantity += int(quantity)
            product.in_stock -= int(quantity)
        elif action == 'delete':
            cart_product.quantity -= int(quantity)
            product.in_stock += int(quantity)

        product.save()
        cart_product.save()

        if cart_product.quantity <= 0:
            cart_product.delete()

    def clear(self):
        cart = self.get_cart_info()['cart']
        cart_products = cart.cartproduct_set.all()
        for product in cart_products:
            product.delete()
        cart.save()

    def apply_coupon(self, coupon_code):
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            cart_total_price = self.get_cart_info()['cart_total_price']
            discount_amount = cart_total_price * (coupon.discount_percentage / 100)
            discounted_price = cart_total_price - discount_amount

            return {
                'discounted_price': discounted_price,
                'coupon': coupon_code,
                'discount_amount': discount_amount
            }
        except:
            return {'error': 'Invalid or inactive coupon code.'}


class CartForAnonymous:
    def __init__(self, request, product_id=None, action=None, color=None, size=None, quantity=1):
        self.session = request.session
        self.cart = self.get_cart()
        self.color = color
        self.size = size
        self.quantity = quantity

        if product_id and action:
            self.key = str(product_id)
            self.product = Product.objects.get(pk=product_id)
            self.cart_product = self.cart.get(self.key)

            if action == 'add' and self.product.in_stock > 0:
                self.add()
            elif action == 'delete':
                self.delete()

            self.product.save()
            self.save()

    def get_cart(self):
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        return cart

    def save(self):
        self.session.modified = True

    def add(self):
        if self.cart_product:
            self.cart_product['quantity'] += self.quantity
        else:
            self.cart[self.key] = {
                'quantity': self.quantity,
                'size': self.size,
                'color': self.color
            }
        self.product.in_stock -= self.quantity

    def delete(self):
        self.cart_product['quantity'] -= self.quantity
        self.product.in_stock += self.quantity
        if self.cart_product['quantity'] <= 0:
            del self.cart[self.key]

    def clear(self):
        self.cart.clear()

    def apply_coupon(self, coupon_code):
        try:
            coupon = Coupon.objects.get(coupon=coupon_code, is_active=True)
            order_info = self.get_cart_info()['cart_total_price']
            discount_amount = order_info * (coupon / 100)
            discounted_price = order_info - discount_amount
            return {
                'discounted_price': discounted_price,
                'coupon': coupon_code,
                'discount_amount': discount_amount
            }
        except:
            return {'error': 'Invalid or inactive coupon code.'}

    def get_cart_info(self):
        products = []
        order = {
            'get_cart_total_price': 0,
            'get_cart_total_quantity': 0,
        }
        cart_total_price = order['get_cart_total_price']
        cart_total_quantity = order['get_cart_total_quantity']

        for key in self.cart:
            if self.cart[key]['quantity'] > 0:
                product_quantity = self.cart[key]['quantity']
                cart_total_quantity += product_quantity
                product = Product.objects.get(pk=key)

                get_total_price = product.get_discount_price() * product_quantity
                cart_product = {
                    'pk': product.pk,
                    'product': {
                        'pk': product.pk,
                        'title': product.title,
                        'price': product.price,
                        'get_discount_price': product.get_discount_price(),
                        'get_first_image': product.get_first_image,
                        'in_stock': product.in_stock,
                    },
                    'quantity': product_quantity,
                    'get_total_price': get_total_price,
                    'size': self.cart[key]['size'],
                    'color': self.cart[key]['color']
                }
                products.append(cart_product)
                order['get_cart_total_price'] += cart_product['get_total_price']
                order['get_cart_total_quantity'] += cart_product['quantity']
                cart_total_price = order['get_cart_total_price']
        self.save()

        return {
            'cart': order,
            'products': products,
            'cart_total_price': cart_total_price,
            'cart_total_quantity': cart_total_quantity,
            'discounted_price': cart_total_price
        }

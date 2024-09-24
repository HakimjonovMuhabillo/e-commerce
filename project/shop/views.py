from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from .utils import CartForAuthenticatedUser, CartForAnonymous
from .models import *
from django.core.paginator import Paginator
from django.db.models import ExpressionWrapper, F, FloatField
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import *


def index(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'articles': Article.objects.all()
    }
    return render(request, 'shop/index.html', context)


class ProductFilter:
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset

    def filter_by_category(self):
        category = self.request.GET.get('category')
        if category:
            self.queryset = self.queryset.filter(category__id=category)
        return self

    def filter_by_brand(self):
        brand = self.request.GET.get('brand')
        if brand:
            self.queryset = self.queryset.filter(brand__id=brand)
        return self

    def filter_by_tag(self):
        tag = self.request.GET.get('tag')
        if tag:
            self.queryset = self.queryset.filter(tag__id=tag)
        return self

    def sort_by(self):
        sort = self.request.GET.get('sort')
        if sort:
            self.queryset = self.queryset.order_by(sort)
        return self

    def paginate(self):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.queryset, 9)
        return paginator.get_page(page)

    def filter_by_price(self):
        price = self.request.GET.get('price')

        self.queryset = self.queryset.annotate(
            discount_price=ExpressionWrapper(
                F('price') - F('price') * F('discount') / 100,
                output_field=FloatField()
            )
        )
        if price:
            if price == '0_50':
                self.queryset = self.queryset.filter(discount_price__gte=0, discount_price__lt=50)
            elif price == '50_100':
                self.queryset = self.queryset.filter(discount_price__gte=50, discount_price__lt=100)
            elif price == '100_150':
                self.queryset = self.queryset.filter(discount_price__gte=100, discount_price__lt=150)
            elif price == '150_200':
                self.queryset = self.queryset.filter(discount_price__gte=150, discount_price__lt=200)
            elif price == '200_250':
                self.queryset = self.queryset.filter(discount_price__gte=200, discount_price__lt=250)
            elif price == 'more_than_250':
                self.queryset = self.queryset.filter(discount_price__gte=250)

        return self

    def get_queryset(self):
        return self.queryset


def shop_view(request):
    products = Product.objects.all()
    product_filter = ProductFilter(request, products)
    products = (
        product_filter
        .filter_by_category()
        .filter_by_price()
        .filter_by_brand()
        .filter_by_tag()
        .sort_by()
        .get_queryset()
    )
    products_count = len(products)
    paginated_products = product_filter.paginate()
    context = {
        'products': paginated_products,
        'products_count': products_count,

    }
    return render(request, 'shop/shop.html', context)


def shop_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(tag=product.tag).exclude(id=product.id)
    sizes = product.size.all()
    colors = product.colors.all()
    form = AddToCartForm(product=product)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product', slug=slug)

    else:
        review_form = ReviewForm()

    reviews = product.reviews.all()
    if reviews.exists():
        rating_list = [i.rating for i in reviews]
        rating = round(sum(rating_list) / len(rating_list), 1)
    else:
        rating = 0
    count_reviews = len(reviews)
    context = {
        'product': product,
        'related_products': related_products,
        'sizes': sizes,
        'review_form': review_form,
        'reviews': product.reviews.all().order_by('-created_at'),
        'rating': rating,
        'count_reviews': count_reviews,
        'colors': colors,
        'form': form
    }
    return render(request, 'shop/shop-details.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()  # Create an empty form for GET requests

    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'shop/login.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def wishlist_view(request):
    user = request.user
    wishs = Wishlist.objects.filter(user=user)
    products = [i.product for i in wishs]
    context = {
        'products': products
    }
    return render(request, 'shop/wishlist.html', context)


def wishlist_action(request, pk):
    product = Product.objects.get(pk=pk)
    user = request.user

    if Wishlist.objects.filter(product=product, user=user).exists():
        wish = Wishlist.objects.get(product=product, user=user)
        wish.delete()
    else:
        Wishlist.objects.create(product=product, user=user)
    return redirect(request.META.get('HTTP_REFERER'))


def account_view(request):
    return render(request, 'shop/account.html')


class SearchView(ListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'

    def get_queryset(self):
        word = self.request.GET.get('q')
        products = Product.objects.filter(title__icontains=word)
        return products


def about_view(request):
    return render(request, 'shop/about.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            contact = form.save()
            return redirect('contact')
    else:
        form = ContactForm()
    context = {
        'form': form
    }
    return render(request, 'shop/contact.html', context)


def blog_view(request):
    articles = Article.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'shop/blog.html', context)


def blog_detail(request, pk):
    article = Article.objects.get(pk=pk)
    comments_count = Comment.objects.filter(article=article).count()

    previous_article = Article.objects.filter(pk__lt=pk).order_by('-pk').first()
    next_article = Article.objects.filter(pk__gt=pk).order_by('pk').first()
    context = {
        'article': article,
        'comments_count': comments_count,
        'comments': Comment.objects.filter(article=article),
        'comment_form': CommentForm(),
        'previous_article': previous_article,
        'next_article': next_article
    }
    return render(request, 'shop/blog-details.html', context)


def save_comment(request, article_id):
    comment_form = CommentForm(data=request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.article = Article.objects.get(pk=article_id)
        comment.user = request.user
        comment.save()
        return redirect('article', article_id)


def to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = AddToCartForm(data=request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity', 1)
            color = form.cleaned_data.get('color', None)
            if color:
                color = color.color.title
            else:
                color = 'No'
            size = form.cleaned_data.get('size', None)
            if size:
                size = size.size.title
            else:
                size = 'No'
            if request.user.is_authenticated:
                CartForAuthenticatedUser(request, product_id, 'add', color, size, quantity)
            else:
                CartForAnonymous(request, product_id, 'add', color, size, quantity)
        else:
            print(form.errors)
    return redirect('product', product.slug)


def plus_minus(request, pk, action, color, size, quantity):
    if request.user.is_authenticated:
        CartForAuthenticatedUser(request, pk, action, color, size, quantity)
    else:
        CartForAnonymous(request, pk, action, color, size, quantity)
    return redirect('cart')


def cart(request):
    if request.user.is_authenticated:
        cart = CartForAuthenticatedUser(request)
    else:
        cart = CartForAnonymous(request)
    cart_info = cart.get_cart_info()
    return render(request, 'shop/shopping-cart.html', cart_info)


def clear(request):
    if request.user.is_authenticated:
        cart = CartForAuthenticatedUser(request)
    else:
        cart = CartForAnonymous(request)
    cart.clear()
    return redirect('cart')


def remove_from_cart(request, product_id, color, size):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart_product = get_object_or_404(CartProduct, cart=cart, product_id=product_id, color=color, size=size)
            product = cart_product.product
            product.in_stock += cart_product.quantity
            product.save()
            cart_product.delete()
        else:
            cart = request.session.get('cart', {})
            key = str(product_id)
            if key in cart:
                quantity = cart[key]['quantity']
                product = Product.objects.get(pk=product_id)
                product.in_stock += quantity
                product.save()
                del cart[key]
            request.session['cart'] = cart

        return redirect('cart')


def apply_coupon_view(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        if request.user.is_authenticated:
            cart = CartForAuthenticatedUser(request)
        else:
            cart = CartForAnonymous(request)

        coupon_result = cart.apply_coupon(coupon_code)
        if 'error' in coupon_result:
            return redirect('cart')
        else:
            messages.success(request, f'Coupon applied! Discount: ${coupon_result["discount_amount"]:.2f}')
    return redirect('cart')


def checkout(request):
    if request.user.is_authenticated:
        cart = CartForAuthenticatedUser(request)
    else:
        cart = CartForAnonymous(request)
    cart_info = cart.get_cart_info()
    context = {
        'shipping_form': ShippingAddressForm(),
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'cart_total_price': cart_info['cart_total_price'],
        'order': cart_info['cart'],
        'products': cart_info['products']
    }
    if not request.user.is_authenticated:
        context['register_form'] = RegisterForm()
    return render(request, 'shop/checkout.html', context)


def process_checkout(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            user_cart = CartForAnonymous(request)
            register_form = RegisterForm(data=request.POST)
            if register_form.is_valid():
                user = register_form.save()
                user.save()
                login(request, user)

        else:
            user_cart = CartForAuthenticatedUser(request)
            user = request.user

        shipping_form = ShippingAddressForm(data=request.POST)
        if shipping_form.is_valid():
            shippingaddress = shipping_form.save(commit=False)
            shippingaddress.user = user
            shippingaddress.save()
        cart_info = user_cart.get_cart_info()
        cart_products = cart_info['products']

        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': cart_product.product.title,
                    'description': cart_product.product.description
                },
                'unit_amount': int(cart_product.product.get_discount_price() * 100)
            },
            'quantity': cart_product.quantity
        } for cart_product in cart_products]
        import stripe
        STRIPE_PUBLISH_KEY = 'pk_test_51PYQY1RvY4iGghS1CIV3oPNQREkgds1Dvj3V2FqhbxKngM5noswtzuRRLKciQS6ZFK1HYFrSDNMhiqESaNahPERU005tT3bvin'
        STRIPE_SECRET_KEY = 'sk_test_51PYQY1RvY4iGghS1nWKS9mUUlKB2h5mRrdFjR1jjG78qxPIRRNKEBP4pubbcMpUMyEMIu7tBBpgWQ2lSAD9dr6si00Jl4JTo3G'
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def success_payment(request):
    cart = CartForAuthenticatedUser(request)
    cart.clear()
    return render(request, 'shop/index.html')

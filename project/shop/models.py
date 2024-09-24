from django.contrib.auth.models import User
from django.db import models
from colorfield.fields import ColorField


class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField()
    information = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    in_stock = models.IntegerField(default=10)

    def get_discount_price(self):
        disc_price = float(self.price) - float(self.price) * self.discount / 100
        return round(disc_price, 2)

    def get_first_image(self):
        if len(self.images.all()) > 0:
            return self.images.first().image.url
        else:
            return 'https://img.freepik.com/premium-vector/photo-coming-soon_77760-116.jpg'

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(max_length=255)
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.title


class Size(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='size')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images', blank=True, null=True)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    text = models.TextField()
    image = models.ImageField(blank=True, null=True, upload_to='reviews')
    created_at = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return f'https://img.freepik.com/premium-vector/photo-coming-soon_77760-116.jpg'

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_cart_total_quantity(self):
        cart_products = self.cartproduct_set.all()
        total_quantity = sum([product.quantity for product in cart_products])
        return total_quantity

    @property
    def get_cart_total_price(self):
        cart_products = self.cartproduct_set.all()
        total_price = sum(product.get_total_price for product in cart_products)
        return total_price


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    color = models.CharField(default='No', max_length=255, blank=True, null=True)
    size = models.CharField(default='No', max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0)

    @property
    def get_total_price(self):
        total_price = (float(self.product.price) - float(
            self.product.price) * self.product.discount / 100) * self.quantity
        return total_price


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)


class Coupon(models.Model):
    code = models.CharField(max_length=100, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


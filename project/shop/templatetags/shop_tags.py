from django import template
from shop.models import Category, Tag, Brand, Wishlist

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.all()


@register.simple_tag()
def get_tags():
    return Tag.objects.all()


@register.simple_tag()
def get_brands():
    return Brand.objects.all()


@register.simple_tag()
def get_sorters():
    return [
        ('title', 'Name (Low To High)'),
        ('title', 'Name ($0 - $55)'),
        ('title', 'Name ($55 - $100)')
    ]


@register.simple_tag()
def query_transform(request, key, value):
    updated = request.GET.copy()
    updated[key] = value
    return updated.urlencode()



@register.simple_tag()
def check_wishlist(request, pk):
    return Wishlist.objects.filter(product_id=pk, user=request.user).exists()
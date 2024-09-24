from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import *
from django.utils.html import format_html


class DiscountFilter(admin.SimpleListFilter):
    title = 'Discount'
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return [
            ('>0', 'Yes')
        ]

    def queryset(self, request, queryset):
        if self.value() == '>0':
            return queryset.filter(discount__gt=0)


@admin.register(Category)
class Category(ModelAdmin):
    list_display = ['id', 'title', 'product_count']
    list_display_links = ['id', 'title']

    def product_count(self, obj):
        return obj.product_set.all().count()


@admin.register(Brand)
class Brand(ModelAdmin):
    list_display = ['id', 'title', 'product_count']
    list_display_links = ['id', 'title']

    def product_count(self, obj):
        return obj.product_set.all().count()


@admin.register(Tag)
class Tag(ModelAdmin):
    list_display = ['id', 'title', 'product_count']
    list_display_links = ['id', 'title']

    def product_count(self, obj):
        return obj.product_set.all().count()


@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ['id', 'title', 'get_color']
    list_editable = ['title']

    def get_color(self, obj):
        return format_html(f'<div style="width:30px; height:30px; background-color: {obj.color};"></div>')


@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ['id', 'title']


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    fk_name = 'product'
    extra = 1


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    fk_name = 'product'
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fk_name = 'product'
    extra = 3


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductColorInline, ProductSizeInline, ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['id', 'title', 'brand', 'category', 'price', 'discount', 'final_price', 'get_first_image']
    list_display_links = ['id', 'title']
    list_editable = ['price', 'discount']
    list_filter = ['category', DiscountFilter]

    def final_price(self, obj):
        disc_price = float(obj.price) - float(obj.price) * obj.discount / 100
        return round(disc_price, 2)

    def get_first_image(self, obj):
        try:
            image = obj.images.first().image.url
            return format_html(f'<img width="100px" src="{image}">')
        except:
            return '-'


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ['id', 'name', 'email', 'message']
    list_display_links = ['id', 'name']


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ['id', 'title', 'category', 'tag', 'brand', 'author']
    list_display_links = ['id', 'title']


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['id', 'code', 'discount_percentage', 'is_active']
    list_editable = ['code', 'discount_percentage', 'is_active']
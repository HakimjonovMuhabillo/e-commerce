from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('shop/', shop_view, name='shop'),
    path('product/<slug:slug>/', shop_detail, name='product'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout', logout_view, name='logout'),
    path('account/', account_view, name='account'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist_action/<int:pk>/', wishlist_action, name='wishlist_action'),
    path('search/', SearchView.as_view(), name='search'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('blog/', blog_view, name='blog'),
    path('article/<int:pk>', blog_detail, name='article'),
    path('comment/<int:article_id>/save/', save_comment, name='save_comment'),
    path('to_cart/<int:product_id>/', to_cart, name='to_cart'),
    path('cart/', cart, name='cart'),
    path('plus_minus/<int:pk>/<str:action>/<str:color>/<str:size>/<int:quantity>', plus_minus, name='plus_minus'),
    path('clear/', clear, name='clear'),
    path('remove-from-cart/<int:product_id>/<str:color>/<str:size>/', remove_from_cart, name='remove_from_cart'),
    path('apply-coupon/', apply_coupon_view, name='apply_coupon_view'),
    path('checkout/', checkout, name='checkout'),
    path('process_checkout/', process_checkout, name='process_checkout'),
    path('payment-success/', success_payment, name='success')
]

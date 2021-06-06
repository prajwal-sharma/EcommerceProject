from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('delete_cart/<int:product_id>/<int:cart_item_id>', views.remove_a_product, name='remove_a_product'),
    path('delete_product/<int:product_id>/<int:cart_item_id>', views.remove_product, name='remove_product'),

    path('checkout/', views.checkout, name='checkout')
]

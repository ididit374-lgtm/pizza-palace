from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('order/', views.place_order, name='place_order'),
    path('order/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pizza_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pizza_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
]
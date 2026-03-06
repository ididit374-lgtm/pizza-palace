from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('order/', views.place_order, name='place_order'),
    path('order/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pizza, Order, OrderItem
from .forms import RegisterForm, EmailLoginForm

# Create your views here.

def menu(request):
    pizzas = Pizza.objects.filter(is_available=True)
    return render(request, 'menu/menu.html', {'pizzas': pizzas})

@login_required(login_url='/login/')
def place_order(request):
    if request.method == 'POST':
        pizza_ids = request.POST.getlist('pizzas')
        if not pizza_ids:
            messages.error(request, 'Please select at least one pizza!')
            return redirect('menu')
        order = Order.objects.create(
            customer_name=request.user.username,
            customer_email=request.user.email
        )
        total = 0
        for pid in pizza_ids:
            pizza = Pizza.objects.get(id=pid)
            OrderItem.objects.create(order=order, pizza=pizza, quantity=1)
            total += pizza.price
        order.total = total
        order.save()
        return redirect('order_confirm', pk=order.pk)
    return redirect('menu')

def order_confirm(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'menu/confirm.html', {'order': order, 'items': items})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! 🍕')
            return redirect('menu')
    else:
        form = RegisterForm()
    return render(request, 'menu/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'menu'))
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailLoginForm()
    return render(request, 'menu/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('menu')

import json

def cart(request):
    cart = request.session.get('cart', {})
    pizzas = []
    total = 0
    for pizza_id, quantity in cart.items():
        try:
            pizza = Pizza.objects.get(id=pizza_id)
            subtotal = pizza.price * quantity
            total += subtotal
            pizzas.append({'pizza': pizza, 'quantity': quantity, 'subtotal': subtotal})
        except Pizza.DoesNotExist:
            pass
    return render(request, 'menu/cart.html', {'pizzas': pizzas, 'total': total})

def add_to_cart(request, pizza_id):
    cart = request.session.get('cart', {})
    key = str(pizza_id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    # Check where the request came from
    next_url = request.GET.get('next', 'menu')
    return redirect(next_url)

def remove_from_cart(request, pizza_id):
    cart = request.session.get('cart', {})
    key = str(pizza_id)
    if key in cart:
        if cart[key] > 1:
            cart[key] -= 1
        else:
            del cart[key]
    request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('menu')
    order = Order.objects.create(
        customer_name=request.user.username,
        customer_email=request.user.email
    )
    total = 0
    for pizza_id, quantity in cart.items():
        pizza = Pizza.objects.get(id=pizza_id)
        OrderItem.objects.create(order=order, pizza=pizza, quantity=quantity)
        total += pizza.price * quantity
    order.total = total
    order.save()
    request.session['cart'] = {}
    return redirect('order_confirm', pk=order.pk)
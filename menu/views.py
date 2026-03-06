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
    return render(request, 'menu/payment.html', {'total': total, 'order_id': order.pk})

def process_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        # Clear cart after payment
        request.session['cart'] = {}
        messages.success(request, '🎉 Payment successful! Your order is being prepared.')
        return redirect('order_confirm', pk=order.pk)
    return redirect('cart')

def gallery(request):
    images = [
        {'url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyyg8huJfraWl0KSeRKyA_Ly55O0f8leSQVA&s', 'title': 'Chicken Tikka Pizza'},
        {'url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGsO8_BXeu1PTx2mLrb7OPazuxz4hJp273FQ&s', 'title': 'Meat Pizza'},
        {'url': 'https://i.pinimg.com/564x/99/6b/03/996b03f80216ead13fa85654c65466ff.jpg', 'title': 'Vegetarian Pizza'},
        {'url': 'https://fivestarps.ca/wp-content/uploads/2025/01/WhatsApp-Image-2025-06-26-at-10.48.24-PM-1.jpeg', 'title': 'Special Pizza'},
        {'url': 'https://www.sainsburysmagazine.co.uk/uploads/media/2400x1800/06/4846-SweetChocolatePizza1120.jpg?v=1-0', 'title': 'Sweet Chocolate Pizza'},
        {'url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTnkP608AAqA2l0Bite6ZP_Mh7cSTD0pg9OLA&s', 'title': 'Pizza Special'},
        {'url': 'https://www.myrelationshipwithfood.com/wp-content/uploads/2017/09/skillet.jpg', 'title': 'Skillet Pizza'},
        {'url': 'https://rated.club/wp-content/uploads/2025/06/Dominos-Chicken-Kickers-review-8-1024x683.jpg', 'title': 'Chicken Kickers'},
        {'url': 'https://tb-static.uber.com/prod/image-proc/processed_images/fb4349f2cf2649c65691b2c636629a63/c67fc65e9b4e16a553eb7574fba090f1.jpeg', 'title': 'Uber Eats Special'},
        {'url': 'https://www.dominos.co.uk/blog/wp-content/uploads/2024/02/Dominos-Potato-Wedges-1.jpg', 'title': 'Potato Wedges'},
        {'url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSN4Igx1QLGcFfv8-QRE1Ta-zevqtYo3fBGJA&s', 'title': 'Pizza Slice'},
        {'url': 'https://www.fountain-filters.co.uk/blog-admin/app/web/upload/source/20_f19a419303daf9a702b5f8c113d4f117.webp', 'title': 'Fresh Pizza'},
    ]
    return render(request, 'menu/gallery.html', {'images': images})
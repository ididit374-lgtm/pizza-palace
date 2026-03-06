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
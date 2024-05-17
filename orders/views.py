from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.shortcuts import render, redirect
from django.db.models import Sum

from .models import Order
from .forms import OrderForm
from .forms import SignUpForm
from .models import Product

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})

@permission_required('orders.can_view_order', raise_exception=True)
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    if order.user != request.user:
        # Handle unauthorized access (e.g., return a 404 page)
        pass
    total_price = order.products.all().aggregate(total_price=Sum('price'))['total_price']
    return render(request, 'orders/order_detail.html', {'order': order, 'total_price': total_price})

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create a new order and associate it with the current user
            order = Order.objects.create(
                user=request.user  # Associate the order with the current user
            )

            # Iterate over the submitted product data to create and assign products to the order
            for i in range(1, 6):  # Adjust the range as needed to handle multiple products
                product_name = form.cleaned_data.get(f'product_name_{i}')
                product_description = form.cleaned_data.get(f'product_description_{i}')
                product_price = form.cleaned_data.get(f'product_price_{i}')

                # Only create a product if all fields are provided
                if product_name and product_description and product_price:
                    product = Product.objects.create(
                        name=product_name,
                        description=product_description,
                        price=product_price,
                        user=request.user  # Associate the product with the current user
                    )
                    # Add the product to the order
                    order.products.add(product)

            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})
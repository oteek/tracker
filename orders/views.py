from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.core.exceptions import PermissionDenied
from django.http import Http404

from django.shortcuts import render, redirect
from django.db.models import Sum

from .models import Order, Product
from .forms import OrderForm, SignUpForm

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

@login_required
@permission_required('orders.view_order', raise_exception=True)
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        # tikrina ar uzsakymas atitinka
        if order.user != request.user:
            raise PermissionDenied("You do not have permission to view this order.")
        total_price = order.products.all().aggregate(total_price=Sum('price'))['total_price']
        return render(request, 'orders/order_detail.html', {'order': order, 'total_price': total_price})
    except PermissionDenied as e:
        return render(request, 'orders/error.html', {'message': str(e)})
    except Order.DoesNotExist:
        return render(request, 'orders/error.html', {'message': "Order does not exist."})

@login_required
@permission_required('orders.add_order', raise_exception=True)
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create a new order and associate it with the current user
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Get the number of products from the form
            num_products = form.cleaned_data.get('num_products', 2)  # Default to 0 if num_products is None

            # Iterate over the submitted product data to create and assign products to the order
            for i in range(1, num_products + 1):  # Adjust the range as needed to handle multiple products
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
                    order.products.add(product)
            
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})


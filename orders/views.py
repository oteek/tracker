from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.forms import modelformset_factory

from django.core.exceptions import PermissionDenied
from django.http import Http404

from django.shortcuts import render, redirect
from django.db.models import Sum

from .models import Order, Product
from .forms import OrderForm, SignUpForm, ProductForm, ProductFormSet

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
        if order.user != request.user:
            # jeigu orderio kurejas neatitinka dabartini prisiloginusi vartotoja, neleidzia jam perziuret to orderio
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
        order_form = OrderForm(request.POST)
        product_formset = ProductFormSet(request.POST, queryset=Product.objects.none())

        if order_form.is_valid() and product_formset.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user
            order.save()

            for form in product_formset:
                product = form.save(commit=False)
                product.user = request.user
                product.save()
                order.products.add(product)

            return redirect('order_list')
    else:
        order_form = OrderForm()
        product_formset = ProductFormSet(queryset=Product.objects.none())

    return render(request, 'orders/create_order.html', {
        'order_form': order_form,
        'product_formset': product_formset,
    })


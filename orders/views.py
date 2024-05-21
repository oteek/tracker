from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate
from django.contrib import messages

from django.forms import modelformset_factory

from django.core.exceptions import PermissionDenied
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum

from .models import Order, Product
from .forms import OrderForm, SignUpForm, ProductForm, ProductFormSet


def get_product_formset(extra):
    return modelformset_factory(Product, form=ProductForm, extra=extra, can_delete=True)

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # turbut bloga strategija jeigu svari duombaze neturi customer grupes bet dabar laiko ir taip nera kazka galvoti
            customer_group = Group.objects.get(name='Customer')
            user.groups.add(customer_group)

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
        product_formset = get_product_formset(extra=1)(request.POST, queryset=Product.objects.none())

        if order_form.is_valid():
            valid_products = False
            for form in product_formset:
                if form.is_valid() and form.cleaned_data.get('name'):
                    valid_products = True
                    break

            if valid_products and product_formset.is_valid():
                order = order_form.save(commit=False)
                order.user = request.user
                order.save()

                for form in product_formset:
                    if form.cleaned_data.get('name'):
                        product = form.save(commit=False)
                        product.user = request.user
                        product.save()
                        order.products.add(product)

                messages.success(request, 'Order created successfully!')
                return redirect('order_list')
            else:
                order_form.add_error(None, "You must add at least one valid product.")
    else:
        order_form = OrderForm()
        product_formset = get_product_formset(extra=1)(queryset=Product.objects.none())

    return render(request, 'orders/create_order.html', {
        'order_form': order_form,
        'product_formset': product_formset,
    })

@login_required
@permission_required('orders.change_order', raise_exception=True)
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        product_formset = ProductFormSet(request.POST, queryset=order.products.all())
        
        if order_form.is_valid() and product_formset.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user
            order.save()

            # Save the products and handle deletions
            for form in product_formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:
                        form.instance.delete()
                else:
                    product = form.save(commit=False)
                    product.user = request.user
                    product.save()
                    order.products.add(product)

            messages.success(request, 'Order edited successfully!')
            return redirect('order_list')
    else:
        order_form = OrderForm(instance=order)
        product_formset = ProductFormSet(queryset=order.products.all())

    return render(request, 'orders/edit_order.html', {
        'order': order,
        'order_form': order_form,
        'product_formset': product_formset,
    })


@login_required
@permission_required('orders.delete_order', raise_exception=True)
def delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.user != request.user:
            raise PermissionDenied("You do not have permission to delete this order.")
        if request.method == 'POST':
            order.products.all().delete()
            order.delete()
            messages.success(request, 'Order deleted successfully!')
            return redirect('order_list')
        return render(request, 'orders/delete_order.html', {'order': order})
    except PermissionDenied as e:
        return render(request, 'orders/error.html', {'message': str(e)})
    except Order.DoesNotExist:
        return render(request, 'orders/error.html', {'message': "Order does not exist."})
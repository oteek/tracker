from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Order
from .forms import OrderForm
from .models import Product

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    total_price = order.products.all().aggregate(total_price=Sum('price'))['total_price']
    return render(request, 'orders/order_detail.html', {'order': order, 'total_price': total_price})


def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Save the form data to get the order instance
            if form.cleaned_data['existing_product']:
                product = form.cleaned_data['existing_product']
            else:
                product_name = form.cleaned_data['product_name']
                product_description = form.cleaned_data['product_description']
                product_price = form.cleaned_data['product_price']
                product = Product.objects.create(name=product_name, description=product_description, price=product_price)
            order.save()  # Save the order instance
            order.products.add(product)
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})
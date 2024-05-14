from django.shortcuts import render
from .models import Order

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})
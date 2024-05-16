from django import forms
from .models import Order, Product

class OrderForm(forms.ModelForm):
    product_name = forms.CharField(max_length=100, required=False, label='Product Name')
    product_description = forms.CharField(widget=forms.Textarea, required=False, label='Product Description')
    product_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Product Price')
    existing_product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label='Existing Product')

    class Meta:
        model = Order
        fields = ['customer', 'product_name', 'product_description', 'product_price', 'existing_product']
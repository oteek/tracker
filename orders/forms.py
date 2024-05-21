from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User

from .models import Order, Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].required = True

ProductFormSet = modelformset_factory(Product, form=ProductForm, extra=0, can_delete=True)
# ProductFormSet = forms.modelformset_factory(Product, form=ProductForm, extra=1)
# ProductFormSet = inlineformset_factory(Order, Product, form=ProductForm, extra=1, can_delete=True)

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
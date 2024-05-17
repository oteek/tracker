from django import forms
from .models import Order, Product
from django.contrib.auth.models import User

class OrderForm(forms.ModelForm):
    product_name = forms.CharField(max_length=100, required=False, label='Product Name')
    product_description = forms.CharField(widget=forms.Textarea, required=False, label='Product Description')
    product_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Product Price')
    # existing_product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label='Existing Product')
    # nera logikos naujiem uzsakymam prisegineti jau esamus produktus duombazej

    class Meta:
        model = Order
        fields = ['product_name', 'product_description', 'product_price']

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
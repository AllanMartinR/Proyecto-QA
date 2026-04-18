from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import Product, Category, CustomUser

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category', 'image', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
		
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """Obtener usuarios por email usando el modelo CustomUser"""
        active_users = CustomUser._default_manager.filter(
            email__iexact=email,
            is_active=True
        )
        return (u for u in active_users if u.has_usable_password())

class CustomSetPasswordForm(SetPasswordForm):
    """Formulario personalizado para establecer nueva contraseña usando CustomUser"""
    pass
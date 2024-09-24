from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    color = forms.ModelChoiceField(queryset=ProductColor.objects.all(), required=False)
    size = forms.ModelChoiceField(queryset=ProductSize.objects.all(), required=False)

    def __init__(self, product, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].queryset = ProductSize.objects.filter(product=product)
        self.fields['color'].queryset = ProductColor.objects.filter(product=product)
        self.fields['quantity'].widget.attrs['data-stock'] = product.in_stock


class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'autofocus': False,
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Имя пользователя'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Пароль'
    }), help_text="")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Подтвердите пароль'
    }), help_text="")

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Почта'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')],
        widget=forms.RadioSelect(attrs={
            'class': 'rating-stars'
        })
    )
    text = forms.Field(widget=forms.Textarea(attrs={
        'class': 'form-control'
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Review
        fields = ['rating', 'text', 'image']


class ContactForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Message'
    }))

    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Comment'
    }))

    class Meta:
        model = Comment
        fields = ['text']


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['country', 'address', 'city', 'state', 'zipcode', 'phone']
        widgets = {
            'country': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vehicle, Enquiry, VehicleCategory


class BuyerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Last name'}))
    email      = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'vw-input', 'placeholder': 'Email address'}))
    phone      = forms.CharField(max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': '+91 XXXXX XXXXX'}))

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'vw-input')


class SellerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Last name'}))
    email      = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'vw-input', 'placeholder': 'Email address'}))
    phone      = forms.CharField(max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': '+91 XXXXX XXXXX'}))
    location   = forms.CharField(max_length=200, required=True,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'City, State'}))
    bio        = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'vw-input', 'rows': '3',
                                     'placeholder': 'Tell buyers about yourself or your business...'}))

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'phone', 'location', 'bio', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'vw-input')


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'vw-input', 'placeholder': 'Password'}))


class AddVehicleForm(forms.ModelForm):
    """
    Full vehicle listing form — all fields including 3 image uploads.
    IMPORTANT: The view must pass request.FILES and use enctype="multipart/form-data".
    """
    class Meta:
        model  = Vehicle
        fields = [
            'title', 'category', 'brand', 'model_name',
            'price', 'original_price',
            'fuel_type', 'year', 'mileage', 'km_driven',
            'condition', 'color', 'engine_cc',
            'description', 'is_negotiable',
            'image', 'image2', 'image3',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'vw-input',
                'placeholder': 'e.g. Honda Activa 6G — Excellent Condition',
            }),
            'category': forms.Select(attrs={'class': 'vw-select'}),
            'brand': forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'e.g. Honda'}),
            'model_name': forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'e.g. Activa 6G'}),
            'price': forms.NumberInput(attrs={
                'class': 'vw-input', 'placeholder': 'Asking price in ₹', 'min': '0',
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'vw-input', 'placeholder': 'MRP / original price (optional)', 'min': '0',
            }),
            'fuel_type': forms.Select(attrs={'class': 'vw-select'}),
            'year': forms.NumberInput(attrs={
                'class': 'vw-input', 'placeholder': 'e.g. 2023', 'min': '1990', 'max': '2026',
            }),
            'mileage': forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'e.g. 45 km/l'}),
            'km_driven': forms.NumberInput(attrs={
                'class': 'vw-input', 'placeholder': '0 if brand new', 'min': '0',
            }),
            'condition': forms.Select(attrs={'class': 'vw-select'}),
            'color': forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'e.g. Pearl White'}),
            'engine_cc': forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'e.g. 110cc or 1497cc'}),
            'description': forms.Textarea(attrs={
                'class': 'vw-input',
                'rows': '5',
                'placeholder': 'Describe your vehicle — condition, features, service history...',
            }),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'vw-checkbox'}),
            # Image fields — allow any image type, render as file inputs
            'image':  forms.ClearableFileInput(attrs={'class': 'vw-file-input', 'accept': 'image/*'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'vw-file-input', 'accept': 'image/*'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'vw-file-input', 'accept': 'image/*'}),
        }
        labels = {
            'title':          'Listing Title',
            'model_name':     'Model',
            'price':          'Asking Price (₹)',
            'original_price': 'Original / MRP Price (₹)',
            'km_driven':      'KM Driven',
            'engine_cc':      'Engine Capacity',
            'is_negotiable':  'Price is negotiable',
            'image':          'Main Photo',
            'image2':         'Photo 2 (optional)',
            'image3':         'Photo 3 (optional)',
        }


class EditVehicleForm(AddVehicleForm):
    """Same as AddVehicleForm but used for editing — images are optional."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required  = False
        self.fields['image2'].required = False
        self.fields['image3'].required = False


class EnquiryForm(forms.ModelForm):
    class Meta:
        model  = Enquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Your full name'}),
            'email':   forms.EmailInput(attrs={'class': 'vw-input', 'placeholder': 'your@email.com'}),
            'phone':   forms.TextInput(attrs={'class': 'vw-input', 'placeholder': '+91 XXXXX XXXXX'}),
            'message': forms.Textarea(attrs={
                'class': 'vw-input', 'rows': '3',
                'placeholder': 'I am interested in this vehicle...',
            }),
        }


class SearchForm(forms.Form):
    q         = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Search brand, model...'}))
    category  = forms.ChoiceField(choices=[], required=False,
        widget=forms.Select(attrs={'class': 'vw-select'}))
    fuel      = forms.ChoiceField(choices=[], required=False,
        widget=forms.Select(attrs={'class': 'vw-select'}))
    min_price = forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'class': 'vw-input', 'placeholder': 'Min ₹'}))
    max_price = forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={'class': 'vw-input', 'placeholder': 'Max ₹'}))
    sort      = forms.ChoiceField(
        choices=[('', 'Latest'), ('price_asc', 'Price ↑'),
                 ('price_desc', 'Price ↓'), ('year_desc', 'Newest Year')],
        required=False,
        widget=forms.Select(attrs={'class': 'vw-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('', 'All Categories')] + [
            (c.slug, c.name) for c in VehicleCategory.objects.all()
        ]
        self.fields['fuel'].choices = [
            ('', 'All Fuels'), ('petrol', 'Petrol'), ('diesel', 'Diesel'),
            ('electric', '⚡ Electric'), ('hybrid', 'Hybrid'), ('cng', 'CNG'),
        ]


class SellerProfileForm(forms.Form):
    """Form for seller to update their profile info and avatar."""
    name     = forms.CharField(max_length=150,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'Your display name'}))
    phone    = forms.CharField(max_length=20,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': '+91 XXXXX XXXXX'}))
    email    = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'vw-input', 'placeholder': 'your@email.com'}))
    location = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'vw-input', 'placeholder': 'City, State'}))
    bio      = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'vw-input', 'rows': '3',
                                     'placeholder': 'Tell buyers about your business...'}))
    avatar   = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'vw-file-input', 'accept': 'image/*'}))

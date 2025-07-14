from django import forms
from app.models import Contact, Review ,Tour ,Place, Food, Culture
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'content', 'rating']
class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'location', 'describe', 'image', 'rating']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'location', 'describe', 'image', 'rating']

class CultureForm(forms.ModelForm):
    class Meta:
        model = Culture
        fields = ['name', 'source', 'describe', 'image', 'rating']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên của bạn'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Nhập nội dung'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')





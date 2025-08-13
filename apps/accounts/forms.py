from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import CustomUser

User = get_user_model()

class RegisterForm(UserCreationForm):

    email = forms.EmailField(label="이메일", required=True)
    address = forms.CharField(label="기본 주소", max_length=200, required=True)
    detail_address = forms.CharField(label="상세 주소", max_length=100, required=True)
    phone = forms.CharField(label="전화번호", max_length=20, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'address', 'detail_address', 'phone')

    @transaction.atomic
    def save(self):

        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]
        user.address = self.cleaned_data["address"]
        user.detail_address = self.cleaned_data["detail_address"]
        user.phone = self.cleaned_data["phone"]
        user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'detail_address', 'gender', 'birth_date']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'detail_address': forms.TextInput(attrs={'class': 'form-control'}),
        }
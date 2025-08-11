from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class UserRegistrationForm(UserCreationForm):
    """
    UserCreationForm을 상속받아 회원가입에 필요한 필드를 추가 정의
    """
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone', 'birth_date', 'gender')

    def clean_email(self):
        """이메일 중복 검사"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용중인 이메일입니다.")
        return email

    def clean_phone(self):
        """전화번호 형식 검증 (예시)"""
        phone = self.cleaned_data.get('phone')
        # 필요시 정규표현식 등으로 유효성 검사 로직 추가
        return phone

class ProfileUpdateForm(forms.ModelForm):
    """
    사용자 프로필 정보 수정을 위한 폼
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # email 필드는 수정 불가하도록 설정 (예시)
        # self.fields['email'].disabled = True

    def clean(self):
        """여러 필드에 걸친 유효성 검사"""
        cleaned_data = super().clean()
        # 복합 유효성 검사 로직 추가 가능
        return cleaned_data

class AddressForm(forms.ModelForm):
    """
    주소 생성을 위한 폼
    """
    class Meta:
        model = Address
        fields = ['name', 'full_address', 'zip_code', 'is_default']

    def clean_zip_code(self):
        """우편번호 유효성 검사 (예시)"""
        zip_code = self.cleaned_data.get('zip_code')
        if not zip_code.isdigit() or len(zip_code) != 5:
            raise forms.ValidationError("올바른 5자리 우편번호를 입력하세요.")
        return zip_code

    def save(self, commit=True):
        """기본 배송지 설정 로직 추가"""
        address = super().save(commit=False)
        if address.is_default:
            address.user.addresses.update(is_default=False)
        if commit:
            address.save()
        return address

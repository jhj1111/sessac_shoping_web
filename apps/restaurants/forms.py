from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    """
    리뷰 작성을 위한 모델 폼
    """
    class Meta:
        model = Review
        # 사용자에게 입력받을 필드만 지정
        fields = ['rating', 'content', 'image']
        widgets = {
            'rating': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5', 'max': '5.0', 'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': '음식과 서비스에 대한 솔직한 리뷰를 남겨주세요!'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
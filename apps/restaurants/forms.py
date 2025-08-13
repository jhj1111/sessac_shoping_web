from django import forms
from .models import Review, ReviewComment

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

class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '고객님의 소중한 리뷰에 정성을 담아 답글을 작성해주세요.'
            }),
        }
        labels = {
            'content': '', # 라벨을 비워 깔끔하게 만듭니다.
        }
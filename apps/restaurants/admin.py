from django.contrib import admin
from .models import Restaurant, MenuCategory, Menu, Review, ReviewComment

# Register your models here.

# 1. ReviewComment를 Review 상세 페이지 안에서 함께 편집할 수 있도록 'Inline'으로 정의
class ReviewCommentInline(admin.StackedInline):
    model = ReviewComment
    extra = 1  # 추가로 입력할 빈 폼의 수
    max_num = 1 # 하나의 리뷰에 하나의 댓글만 달 수 있도록 설정 (OneToOneField)
    can_delete = False # 인라인에서는 댓글 삭제를 비활성화

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Review 모델에 대한 관리자 페이지 설정
    """
    list_display = ('restaurant', 'user', 'rating', 'created_at', 'has_comment')
    list_filter = ('restaurant', 'rating')
    search_fields = ('user__username', 'content')
    readonly_fields = ('user', 'restaurant', 'rating', 'content', 'image', 'created_at', 'updated_at')

    # 2. Review 상세 페이지에 위에서 만든 ReviewCommentInline을 포함시킴
    inlines = [ReviewCommentInline]

    @admin.display(description='사장님 댓글 여부', boolean=True)
    def has_comment(self, obj):
        return hasattr(obj, 'comment')

# 나머지 모델들도 간단하게 등록
admin.site.register(Restaurant)
admin.site.register(MenuCategory)
admin.site.register(Menu)
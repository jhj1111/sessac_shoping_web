from django.db import models
from django.conf import settings
from django.utils import timezone  # timezone.now() 사용을 위해 추가

from apps.accounts.models import Address


class Restaurant(models.Model):
    CATEGORY_CHOICES = [
        ('korea', '한식'),
        ('china', '중식'),
        ('japan', '일식'),
        ('usa', '양식'),
        ('dessert', '디저트'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    category = models.CharField(max_length=50)
    operating_hours = models.JSONField(default=dict)
    minimum_order = models.PositiveIntegerField(default=15000)
    delivery_fee = models.PositiveIntegerField(default=3000)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)
    is_open = models.BooleanField(default=True)
    owner_notice = models.TextField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def calculate_distance(self, user_lat, user_lon):
        # Placeholder for distance calculation logic
        pass

    def is_currently_open(self):
        # Placeholder for checking opening hours
        pass

    def update_rating(self):
        # Placeholder for rating update logic
        pass

    def update_review_statistics(self):
        reviews = self.reviews.all()
        self.review_count = reviews.count()
        self.rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0.0
        self.save(update_fields=['review_count','rating'])

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField("별점", max_digits=2, decimal_places=1)
    content = models.TextField("리뷰 내용")
    image = models.ImageField(
        "리뷰 사진",
        upload_to='review_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.restaurant.name} 리뷰: {self.user.username} ({self.rating})'

    @property
    def operating_status(self):
        """
        JSONField로 저장된 운영 시간을 바탕으로 현재 영업 상태를 반환합니다.
        """
        now = timezone.now()
        current_time_str = now.strftime("%H:%M")
        weekday_str = now.strftime("%a").upper()

        today_hours = self.operating_hours.get(weekday_str)
        if not today_hours or len(today_hours) != 2:
            return "영업 정보 없음"

        start_time_str, end_time_str = today_hours

        # 자정을 넘어가는 시간 처리 (예: 22:00 ~ 02:00)
        if start_time_str > end_time_str:
            if current_time_str >= start_time_str or current_time_str < end_time_str:
                return "영업 중"
            else:
                return "영업 준비 중"
        # 일반적인 시간 처리
        else:
            if start_time_str <= current_time_str < end_time_str:
                return "영업 중"
            else:
                return "영업 준비 중"


    def update_review_statistics(self):
        """리뷰 통계(개수, 평균 별점)를 업데이트합니다."""
        reviews = self.reviews.all()
        self.review_count = reviews.count()
        self.average_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0.0
        self.save(update_fields=['review_count', 'average_rating'])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.restaurant.update_review_statistics()

    def delete(self, *args, **kwargs):
        restaurant = self.restaurant
        super().delete(*args, **kwargs)
        restaurant.update_review_statistics()

class ReviewComment(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField("댓글 내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    def __str__(self):
        return f'{self.review}에 대한 사장님 댓글'

# II. 메뉴 및 옵션 (Menu & Options)
class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField("카테고리명", max_length=20)
    order = models.PositiveIntegerField("표시 순서", default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "메뉴 카테고리"
        verbose_name_plural = "메뉴 카테고리들"

    def __str__(self):
        return f'[{self.restaurant.name}] {self.name}'

class Menu(models.Model):
    # restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='restaurants/menu_images/', blank=True, null=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='menus', null=True, default=1)
    is_popular = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.category and self.category.restaurant:
            return f'[{self.category.restaurant.name}] {self.name}'  # ✅ self.category.restaurant 사용
        return self.name

    def get_formatted_price(self):
        # Placeholder for price formatting
        return f'{self.price}원'

    def toggle_availability(self):
        self.is_available = not self.is_available
        self.save()


class OptionGroup(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='option_groups')
    name = models.CharField("옵션 그룹명", max_length=20)
    is_mandatory = models.BooleanField("필수 선택 여부", default=False)

    def __str__(self):
        return f'{self.menu.name} - {self.name}'


class Option(models.Model):
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE, related_name='options')
    name = models.CharField("옵션명", max_length=20)
    extra_price = models.PositiveIntegerField("추가 금액", default=0)

    def __str__(self):
        return f'{self.option_group.name} - {self.name} (+{self.extra_price}원)'


    def calculate_price(self, selected_choices):
        # Placeholder for price calculation based on selected options
        pass

class Post(models.Model):
        pass
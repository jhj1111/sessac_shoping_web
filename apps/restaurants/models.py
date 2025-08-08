import datetime
from django.db import models
from django.db.models import Avg
from django.conf import settings

# I. 음식점 정보 (Restaurant Information)
class Restaurant(models.Model):
    # --- 기본 정보 ---
    name = models.CharField("가게명", max_length=20)
    notice = models.TextField("사장님 공지", blank=True)
    operating_hours = models.CharField(
        "운영시간",
        max_length=255,
        blank=True,
        null=True
    )
    address = models.CharField("주소", max_length=40)
    min_order_price = models.PositiveIntegerField(
        "최소 주문 금액",
        default=15000
    )
    delivery_tip = models.PositiveIntegerField("배달 팁", default=4000)

    # --- 추가 정보 ---
    origin_info = models.TextField("원산지 정보", blank=True)

    # --- 지도 정보 ---
    latitude = models.DecimalField(
        "위도",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    @property
    def operating_status(self):
        now = datetime.datetime.now().time()
        start, end = datetime.time(9, 0), datetime.time(21, 0)
        return "영업 중" if start <= now <= end else "영업 준비 중"

    @property
    def total_reviews(self):
        return self.reviews.count()

    @property
    def average_rating(self):
        # 리뷰가 없으면 0.0을 반환
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0

    def __str__(self):
        return self.name


# II. 메뉴 및 옵션 (Menu & Options)
class MenuCategory(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_categories'
    )
    name = models.CharField("카테고리명", max_length=20)
    order = models.PositiveIntegerField("표시 순서", default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'[{self.restaurant.name}] {self.name}'


class Menu(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menus'
    )
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField("메뉴명", max_length=20)
    description = models.TextField("메뉴 설명", blank=True)
    image = models.ImageField("메뉴 사진", upload_to='menu_images/', blank=True)
    price = models.PositiveIntegerField("가격")
    is_signature = models.BooleanField("대표 메뉴 여부", default=False)
    is_popular = models.BooleanField("인기 메뉴 여부", default=False)

    def __str__(self):
        return self.name


class OptionGroup(models.Model):
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='option_groups'
    )
    name = models.CharField("옵션 그룹명", max_length=50)
    is_mandatory = models.BooleanField("필수 선택 여부", default=False)

    def __str__(self):
        return f'{self.menu.name} - {self.name}'


class Option(models.Model):
    option_group = models.ForeignKey(
        OptionGroup,
        on_delete=models.CASCADE,
        related_name='options'
    )
    name = models.CharField("옵션명", max_length=50)
    extra_price = models.PositiveIntegerField("추가 금액", default=0)

    def __str__(self):
        return f'{self.option_group.name} - {self.name} (+{self.extra_price}원)'


# III. 별점 및 리뷰 (Rating & Reviews)
class Review(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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


class ReviewComment(models.Model):
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    content = models.TextField("댓글 내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    def __str__(self):
        return f'{self.review}에 대한 사장님 댓글'
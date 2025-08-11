from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# User 모델은 Django의 기본 User 모델을 확장하여 사용합니다.
class User(AbstractUser):
    # 기존 AbstractUser에 있는 필드(username, email 등) 외에 추가할 필드를 정의
    phone = models.CharField("연락처", max_length=15, blank=True)
    birth_date = models.DateField("생년월일", null=True, blank=True)
    gender = models.CharField("성별", max_length=10, blank=True)
    grade = models.CharField("회원 등급", max_length=20, default='일반')

    # --- 아래 두 필드를 추가하여 related_name 충돌을 해결합니다 ---
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="user_account_groups",  # 기본값 'user_set' 대신 고유한 이름으로 변경
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_account_permissions", # 기본값 'user_set' 대신 고유한 이름으로 변경
        related_query_name="user",
    )

    # AbstractUser의 email 필드를 필수 항목으로 변경하려면 아래 주석을 해제
    # email = models.EmailField('email address', unique=True)

    def get_full_name(self):
        return super().get_full_name()

    def get_grade_benefits(self):
        # 등급별 혜택 로직
        pass

    def update_profile(self, **kwargs):
        # 프로필 업데이트 로직
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField("주소 별칭", max_length=50)  # 예: 집, 회사
    full_address = models.TextField("전체 주소")
    zip_code = models.CharField("우편번호", max_length=10)
    latitude = models.DecimalField("위도", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("경도", max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField("기본 배송지", default=False)

    def __str__(self):
        return f'{self.user.username}의 배송지: {self.name}'

    def set_as_default(self):
        # 모든 주소를 기본 배송지 '아님'으로 설정 후, 현재 주소만 '기본'으로 설정
        self.user.addresses.update(is_default=False)
        self.is_default = True
        self.save()


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField("결제 수단 종류", max_length=20)  # 예: 신용카드, 카카오페이
    card_number = models.CharField("카드 번호", max_length=20)  # 암호화 필요
    card_name = models.CharField("카드사/은행명", max_length=30)
    expiry_date = models.DateField("만료일", null=True, blank=True)
    is_default = models.BooleanField("기본 결제수단", default=False)

    def __str__(self):
        return f'{self.user.username}의 결제수단: {self.card_name}'

    def mask_card_number(self):
        # 카드번호 마스킹 로직
        return self.card_number[:4] + "-****-****-" + self.card_number[-4:]
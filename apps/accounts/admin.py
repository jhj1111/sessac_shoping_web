from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address, PaymentMethod

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """커스텀 User 모델을 위한 Admin 클래스"""
    # 기존 UserAdmin의 fieldsets에 커스텀 필드 추가
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('phone', 'birth_date', 'gender', 'grade')}),
    )
    # 기존 UserAdmin의 add_fieldsets에 커스텀 필드 추가
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('phone', 'birth_date', 'gender', 'grade')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'grade')
    list_filter = UserAdmin.list_filter + ('grade',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Address 모델을 위한 Admin 클래스"""
    list_display = ('user', 'name', 'full_address', 'zip_code', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('user__username', 'full_address', 'zip_code')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """PaymentMethod 모델을 위한 Admin 클래스"""
    list_display = ('user', 'type', 'card_name', 'mask_card_number', 'is_default')
    list_filter = ('type', 'is_default')
    search_fields = ('user__username', 'card_name')

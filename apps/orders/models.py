from django.db import models
from django.conf import settings
from django.utils import timezone

# 순환 참조를 피하기 위해 문자열로 모델을 참조합니다.
# from apps.restaurants.models import Restaurant, Menu
# from apps.accounts.models import Address

class Cart(models.Model):
    """
    사용자가 주문하기 전, 메뉴를 담아두는 장바구니 모델
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    # [변경] Cart가 특정 가게에 종속되지 않도록 restaurant 필드를 완전히 제거합니다.
    # 이제 이 장바구니에는 여러 가게의 메뉴를 담을 수 있습니다.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_item(self, menu, quantity, options=None):
        """장바구니에 아이템을 추가합니다."""
        # [논리 추가] 다른 가게의 메뉴를 담을 때의 정책을 결정할 수 있습니다.
        # 예: self.items.first().menu.restaurant != menu.restaurant 라면 clear() 또는 예외 발생
        # 현재는 여러 가게 메뉴를 자유롭게 담는 것을 허용합니다.
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            menu=menu,
            selected_options=options or {}
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return cart_item

    def remove_item(self, cart_item_id):
        """장바구니에서 아이템을 제거합니다."""
        CartItem.objects.filter(id=cart_item_id, cart=self).delete()

    def get_total_price(self):
        """장바구니의 총 금액을 계산합니다."""
        return sum(item.get_item_total() for item in self.items.all())

    def clear(self):
        """장바구니를 비웁니다."""
        self.items.all().delete()

    def is_empty(self):
        """장바구니가 비었는지 확인합니다."""
        return not self.items.exists()

    def __str__(self):
        return f"{self.user.username}님의 장바구니"


class CartItem(models.Model):
    """
    장바구니에 담긴 개별 메뉴 항목
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey('restaurants.Menu', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    selected_options = models.JSONField(default=dict, blank=True)

    def get_item_total(self):
        """아이템의 총 가격을 계산합니다."""
        # 옵션 가격 등을 고려한 복잡한 계산이 필요할 수 있습니다.
        return self.menu.price * self.quantity

    def __str__(self):
        return f"{self.cart.user.username}의 장바구니 항목: {self.quantity}"


class Order(models.Model):
    """
    사용자의 최종 주문 정보를 저장하는 핵심 모델
    하나의 주문에 여러 가게의 메뉴(OrderItem)가 포함될 수 있습니다.
    """
    class OrderStatus(models.TextChoices):
        PENDING = '주문 대기'
        COOKING = '조리 중'
        DELIVERING = '배송 중'
        DELIVERED = '배송 완료'
        CANCELLED = '주문 취소'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # [변경] Order가 특정 가게에 종속되지 않도록 restaurant 필드를 완전히 제거합니다.
    # address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    # [변경] 이 필드들은 모든 가게의 주문 항목을 합산한 총계가 됩니다.
    total_amount = models.PositiveIntegerField(default=0, help_text="모든 가게의 주문 총액")
    delivery_fee = models.PositiveIntegerField(default=0, help_text="모든 가게의 배달비 총액")
    discount_amount = models.PositiveIntegerField(default=0)
    
    order_time = models.DateTimeField(auto_now_add=True)
    
    special_requests = models.TextField(blank=True, help_text="모든 가게에 대한 공통 요청사항")
    payment_method = models.CharField(max_length=50, default='card')

    @property
    def restaurants(self):
        """이 주문에 포함된 모든 가게의 목록을 반환합니다."""
        return list(set(item.menu.restaurant for item in self.items.all()))

    def group_items_by_restaurant(self):
        """
        주문 항목들을 가게별로 그룹화하여 반환합니다.
        ex) {<Restaurant A 객체>: [<OrderItem 1>, <OrderItem 2>], <Restaurant B 객체>: [<OrderItem 3>]}
        """
        from collections import defaultdict
        # grouped_items = defaultdict(list)
        grouped_items = {}
        for item in self.items.all():
            # grouped_items[item.menu.restaurant].append(item)
            grouped_items[item.menu.restaurant] = grouped_items.get(item.menu.restaurant, []) + [item]
        return grouped_items
    
    


    def __str__(self):
        return f"주문 #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    주문에 포함된 개별 메뉴 항목.
    이 모델은 변경할 필요가 없습니다. 이미 Menu를 통해 Restaurant 정보에 접근할 수 있습니다.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey('restaurants.Menu', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField() # 주문 시점의 가격
    total_price = models.PositiveIntegerField()
    selected_options = models.JSONField(default=dict)

    # [추가] 편의를 위해 restaurant 속성을 추가합니다.
    @property
    def restaurant(self):
        return self.menu.restaurant

    def __str__(self):
        try :
            return f"주문 #{self.order.id}의 항목: {self.menu.name}"
        except AttributeError:
            return "restaurant 미등록"

# --- 아래 모델들은 현재 구조에서 변경할 필요가 없습니다. ---
# 하지만, Delivery 모델은 Order가 아닌, 가게별 주문 단위로 배송이 이루어져야 하므로
# 추가적인 리팩토링이 필요할 수 있습니다. (예: Order 대신 'SubOrder' 같은 모델과 연결)

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_info')
    # ... (이하 생략)

class Rider(models.Model):
    name = models.CharField(max_length=100)
    # ... (이하 생략)

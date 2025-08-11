from ..restaurants.models import Restaurant, Menu
from .models import Order, OrderItem, Cart, CartItem
from ..accounts.models import Address
from django.shortcuts import get_object_or_404


class OrderService:
    @staticmethod
    def create_order(user, cart, address, payment_method, special_requests):
        """
        장바구니 정보를 기반으로 주문을 생성합니다.
        """
        # 1. 주문 유효성 검증 (e.g. 재고 확인)
        OrderService.validate_order(cart)
        
        # 2. 배달비 계산
        # delivery_fee = OrderService.calculate_delivery_fee(address)
        
        # 3. Order 객체 생성
        order = Order.objects.create(
            user=user,
            # delivery_fee=delivery_fee,
            special_requests=special_requests,
            payment_method=payment_method
        )
        
        # 4. CartItem -> OrderItem으로 복사
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu=cart_item.menu,
                quantity=cart_item.quantity,
                unit_price=cart_item.menu.price,
                total_price=cart_item.get_item_total(),
                selected_options=cart_item.selected_options
            )
        
        # 5. 최종 금액 계산
        order.calculate_total()
        
        # 6. 결제 처리
        OrderService.process_payment(order)
        
        # 7. 장바구니 비우기
        cart.clear()
        
        return order

    @staticmethod
    def calculate_delivery_fee(address):
        """주소에 따라 배달비를 계산합니다."""
        # 실제로는 주소 기반으로 복잡한 로직이 필요
        return 3000

    @staticmethod
    def validate_order(cart):
        """주문 생성 전, 재고나 주문 정보에 문제가 없는지 검증합니다."""
        # 예: 각 CartItem의 재고 확인 로직
        pass

    @staticmethod
    def process_payment(order):
        """외부 결제 서비스와 연동하여 결제를 처리합니다."""
        # PG사 연동 로직
        # 결제 성공 시 order.status를 'processing'으로 변경
        pass

class CartService:
    @staticmethod
    def validate_items(cart):
        """장바구니에 담긴 상품들이 현재 판매 가능한 상태인지 확인합니다."""
        # 품절, 단종 등 확인
        pass

    @staticmethod
    def create_order_from_cart_data(user, restaurant_pk, cart_items):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        total_price = 0
        menus = []

        for item_data in cart_items:
            menu = get_object_or_404(Menu, pk=item_data['menu_id'])
            quantity = item_data['quantity']
            total_price += menu.price * quantity
            menus.append({'menu': menu, 'quantity': quantity, 'price': menu.price})

        # 기본 주소를 사용하거나, 주소 선택 로직 필요
        address = user.addresses.first()
        if not address:
            raise Exception("주소 정보가 없습니다. 마이페이지에서 주소를 등록해주세요.")

        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            address=address.address, # 주소 모델의 address 필드 사용
            total_price=total_price,
            payment_method='CARD' # 기본값 설정 또는 사용자 선택
        )

        for menu_data in menus:
            OrderItem.objects.create(
                order=order,
                menu=menu_data['menu'],
                quantity=menu_data['quantity'],
                price=menu_data['price']
            )
        
        return order

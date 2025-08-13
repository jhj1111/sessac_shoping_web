from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse # Import JsonResponse
from django.views.decorators.csrf import csrf_exempt # For AJAX POST without CSRF token (for testing, not recommended for production)
from django.utils.decorators import method_decorator # To apply csrf_exempt to CBV
from django.urls import reverse

import json
from .models import Cart, Order
from .services import OrderService, CartService
from ..restaurants.models import Menu

class OrderCancelAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            order_id = kwargs.get('order_id')
            order = get_object_or_404(Order, id=order_id, user=request.user)

            if order.status != '주문 대기':
                return JsonResponse({'success': False, 'message': '주문 대기 상태에서만 취소가 가능합니다.'})

            order.status = '주문 취소'
            order.save()

            return JsonResponse({'success': True, 'message': '주문이 성공적으로 취소되었습니다.'})

        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': '주문을 찾을 수 없습니다.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


class CartView(LoginRequiredMixin, View):
    """
    장바구니 조회(GET) 및 아이템 추가(POST) 처리
    """
    template_name = 'orders/cart_detail.html'

    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        # 가게별로 아이템을 그룹화하고 소계를 계산하는 로직을 추가합니다.
        context = {
            'cart': cart,
            'grouped_items': cart.group_items_by_restaurant(),
        }
        return render(request, self.template_name, context)

        # context = {
        #     'cart': cart,
        #     'cart_items': cart_items,
        #     'cart_total': cart_total,
        #     'cart_count': cart_count,
        # }
        # return render(request, self.template_name, context)
    def post(self, request, *args, **kwargs):
        # 로그인하지 않은 사용자에 대한 추가 방어
        print('OrderAPIView start')
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'}, status=401)

        try:
            print('try loads data')
            data = json.loads(request.body)
            print('loaded data')
            cart_items = data.get('cart_items', [])
            print(f'cart_items : {cart_items}')
            restaurant_pk = data.get('restaurant_pk')

            if not cart_items or not restaurant_pk:
                return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)

            cart = CartService.create_order_from_cart_data(
                user=request.user,
                restaurant_pk=restaurant_pk,
                cart_items=cart_items,
                )

            print('succeded create order')

            # 성공 응답 반환
            # mypage_orders.html을 사용한다고 가정
            redirect_url = reverse('orders:cart_view') # 주문 상세 페이지 URL로 변경 가능
            return JsonResponse({'success': True, 'redirect_url': redirect_url})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '잘못된 형식의 요청입니다.'}, status=400)
        except Exception as e:
            # 기타 예외 처리
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

        
        return redirect('/mypage/')
    
    
        

class CartDeleteView(LoginRequiredMixin, DeleteView):
    model = Cart
    # success_url = reverse('orders:cart_view')
    
    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.clear()
        # return redirect(reverse('mypage:mypage_main'))
        return redirect(reverse('orders:cart_view'))


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    장바구니 기반 주문 생성(GET, POST)
    """
    model = Order
    template_name = 'orders/order_form.html'
    # fields = ['address', 'special_requests', 'payment_method'] # 예시 필드
    fields = ['special_requests', 'payment_method'] # 예시 필드
    # success_url = reverse_lazy('orders:order_complete') # 주문 완료 페이지로 이동
    success_url = reverse_lazy('') # 임시

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # 로그인한 유저의 주소록만 선택지에 표시
        # form.fields['address'].queryset = self.request.user.addresses.all()
        return form

    def form_valid(self, form):
        cart = get_object_or_404(Cart, user=self.request.user)
        if cart.is_empty():
            form.add_error(None, "장바구니가 비어있습니다.")
            return self.form_invalid(form)

        # 서비스 레이어를 통해 주문 생성
        order = OrderService.create_order(
            user=self.request.user,
            cart=cart,
            address=form.cleaned_data['address'],
            payment_method=form.cleaned_data['payment_method'],
            special_requests=form.cleaned_data['special_requests']
        )
        self.object = order
        return redirect(self.get_success_url())



class OrderAPIView(LoginRequiredMixin, View):
    """
    AJAX 요청을 처리하여 서버의 장바구니로부터 주문을 생성하는 API 뷰
    """
    def post(self, request, *args, **kwargs):
        try:
            cart = get_object_or_404(Cart, user=request.user)
            if cart.is_empty():
                return JsonResponse({'success': False, 'error': '장바구니가 비어있습니다.'}, status=400)

            # 서비스 레이어를 통해 주문 생성
            order = OrderService.create_order(
                user=request.user,
                cart=cart
            )

            # 주문 성공 후, 생성된 주문의 상세 페이지로 이동할 URL을 반환
            # 이 기능을 위해 'orders:order_detail' URL 패턴이 필요합니다.
            # redirect_url = reverse('orders:order_detail', kwargs={'pk': order.pk})
            redirect_url = reverse('mypage:mypage_orders')
            return JsonResponse({'success': True, 'redirect_url': redirect_url})

        except Exception as e:
            # 실제 운영 환경에서는 print 대신 logging을 사용해야 합니다.
            print(f"Order creation failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


# 새로 추가할 API 뷰들
class CartAddAPIView(LoginRequiredMixin, View):
    """장바구니 아이템 추가 API"""

    def post(self, request):
        try:
            menu_id = request.POST.get('menu_id')  # product_id 대신 menu_id 사용
            quantity = int(request.POST.get('quantity', 1))
            options = request.POST.get('options', {})

            menu = get_object_or_404(Menu, id=menu_id)
            cart, created = Cart.objects.get_or_create(user=request.user)

            # CartService 사용
            CartService.add_item_to_cart(
                cart=cart,
                menu=menu,
                quantity=quantity,
                options=options
            )

            # 업데이트된 장바구니 정보
            cart_items = cart.items.all()
            cart_total = sum(item.total_price for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'message': f'{menu.name}이(가) 장바구니에 추가되었습니다.',
                'cart_count': cart_count,
                'cart_total': float(cart_total)
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '장바구니 추가 중 오류가 발생했습니다.'
            }, status=400)


class CartUpdateAPIView(LoginRequiredMixin, View):
    """장바구니 아이템 수량 업데이트 API"""

    def post(self, request):
        try:
            cart_item_id = request.POST.get('cart_item_id')
            quantity = int(request.POST.get('quantity'))

            cart = get_object_or_404(Cart, user=request.user)

            # CartService 사용
            if quantity > 0:
                CartService.update_item_quantity(
                    cart=cart,
                    item_id=cart_item_id,
                    quantity=quantity
                )
            else:
                CartService.remove_item_from_cart(
                    cart=cart,
                    item_id=cart_item_id
                )

            # 업데이트된 장바구니 정보
            cart_items = cart.items.all()
            cart_total = sum(item.get_item_total() for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'cart_total': float(cart_total)
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '수량 업데이트 중 오류가 발생했습니다.'
            }, status=400)


class CartRemoveAPIView(LoginRequiredMixin, View):
    """장바구니 아이템 제거 API"""

    def post(self, request):
        try:
            cart_item_id = request.POST.get('cart_item_id')
            cart = get_object_or_404(Cart, user=request.user)

            # 아이템 이름 가져오기 (메시지용)
            cart_item = cart.items.get(id=cart_item_id)
            item_name = cart_item.menu.name

            # CartService 사용
            CartService.remove_item_from_cart(
                cart=cart,
                item_id=cart_item_id
            )

            # 업데이트된 장바구니 정보
            cart_items = cart.items.all()
            cart_total = sum(item.get_item_total() for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)

            return JsonResponse({'success': True,
                                 'message': f'{item_name}이(가) 장바구니에서 제거되었습니다.', 
                                 'cart_count': int(cart_count), 
                                 'cart_total': float(cart_total)
                                 }, 
                                 safe=False
                                )

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '아이템 제거 중 오류가 발생했습니다.'
            }, status=400)


class CartDataAPIView(LoginRequiredMixin, View):
    """장바구니 데이터 조회 API"""

    def get(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.all()
            cart_data = []

            for item in cart_items:
                cart_data.append({
                    'id': item.id,
                    'menu_id': item.menu.id,  # product_id 대신 menu_id
                    'product_name': item.menu.name,  # menu name
                    'product_price': float(item.menu.price),
                    'quantity': item.quantity,
                    'total_price': float(item.total_price),
                    'product_image': item.menu.image.url if hasattr(item.menu, 'image') and item.menu.image else '',
                    'options': item.options  # 옵션 정보도 포함
                })

            cart_total = sum(item.total_price for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)

            return JsonResponse({
                'cart_items': cart_data,
                'cart_total': float(cart_total),
                'cart_count': cart_count
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '장바구니 데이터 로드 중 오류가 발생했습니다.'
            }, status=400)


class CartClearAPIView(LoginRequiredMixin, View):
    """장바구니 전체 비우기 API"""

    def post(self, request):
        try:
            cart = get_object_or_404(Cart, user=request.user)

            # CartService 사용
            CartService.clear_cart(cart)

            return JsonResponse({
                'success': True,
                'message': '장바구니가 비워졌습니다.',
                'cart_count': 0,
                'cart_total': 0
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '장바구니 비우기 중 오류가 발생했습니다.'
            }, status=400)


# 메뉴 목록 뷰 (상품 목록 대신)
class MenuListView(View):
    """레스토랑별 메뉴 목록"""
    template_name = 'orders/menu_list.html'

    def get(self, request, restaurant_pk):
        from ..restaurants.models import Restaurant
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        menus = Menu.objects.filter(restaurant=restaurant, is_available=True)

        context = {
            'restaurant': restaurant,
            'menus': menus  # products 대신 menus
        }

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = cart.items.all()
            context.update({
                'cart_items': cart_items,
                'cart_total': sum(item.total_price for item in cart_items),
                'cart_count': sum(item.quantity for item in cart_items)
            })
        else:
            context.update({
                'cart_items': [],
                'cart_total': 0,
                'cart_count': 0
            })

        return render(request, self.template_name, context)



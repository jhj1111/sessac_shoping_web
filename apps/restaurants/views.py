import json
from django.utils import timezone

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from apps.restaurants.models import Post
from django.shortcuts import render
from django.views.generic import TemplateView

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import Restaurant, Menu
from apps.orders.models import Order, OrderItem
from .forms import ReviewForm
# 'accounts' 앱의 Address 모델을 가져옵니다. 앱 구조에 맞게 수정이 필요할 수 있습니다.
from apps.accounts.models import Address

def post_list(request):
    return render(request, template_name='main/base.html')


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'main/post_list.html'



class MainDetailView(TemplateView):
    #model = Post
    template_name = 'main/post_main_detail.html'
    # 특정 상세 페이지가 아니라서 이렇게만 하면 이동

# 상세 페이지
class RestaurantListView(ListView):
    """
    모든 음식점 목록을 보여주는 메인 페이지
    """
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 10  # 한 페이지에 10개의 가게를 보여줍니다.


class RestaurantDetailView(DetailView):
    """
    특정 음식점의 상세 정보(메뉴, 리뷰 등)를 보여주는 페이지
    """
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 리뷰 작성 폼을 컨텍스트에 추가
        context['review_form'] = ReviewForm()
        # 해당 가게의 리뷰 목록을 컨텍스트에 추가
        context['reviews'] = self.object.reviews.select_related('user', 'comment').all()
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm

    def form_valid(self, form):
        # ✅ 중복 확인 로직 없이, 바로 저장하는 원래 코드로 복구
        review = form.save(commit=False)
        review.user = self.request.user
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_pk'])
        review.restaurant = restaurant
        review.save() # 바로 저장
        return redirect('restaurants:restaurant_detail', pk=restaurant.pk)

    def form_invalid(self, form):
        restaurant_pk = self.kwargs['restaurant_pk']
        return redirect('restaurants:restaurant_detail', pk=restaurant_pk)


class OrderCreateView(LoginRequiredMixin, View):
    """
    주문을 생성하는 API 형태의 뷰 (AJAX/Fetch 요청으로 호출)
    """

    def post(self, request, *args, **kwargs):
        # AJAX 요청이 아닌 경우 에러 응답
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request'}, status=400)

        try:
            data = json.loads(request.body)
            restaurant_pk = data.get('restaurant_pk')
            cart_items = data.get('cart_items')  # [{'menu_id': 1, 'quantity': 2, 'options': {}}, ...]

            if not all([restaurant_pk, cart_items]):
                return JsonResponse({'error': 'Missing data'}, status=400)

            restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
            # 사용자의 기본 배송지를 가져옵니다.
            user_address = Address.objects.filter(user=request.user, is_default=True).first()
            if not user_address:
                return JsonResponse({'error': '기본 배송지를 설정해주세요.'}, status=400)

            # 데이터베이스 트랜잭션 시작
            with transaction.atomic():
                total_price = 0
                order_items_to_create = []

                for item in cart_items:
                    menu = get_object_or_404(Menu, pk=item['menu_id'])
                    quantity = item['quantity']
                    price_per_item = menu.price

                    # 옵션 가격 계산 (간단한 예시)
                    # 실제 구현 시에는 Option 모델과 연동하여 정확히 계산해야 합니다.
                    options_price = sum(item.get('options', {}).values())
                    total_price += (price_per_item + options_price) * quantity

                    order_items_to_create.append(
                        OrderItem(
                            menu=menu,
                            quantity=quantity,
                            price_per_item=price_per_item,
                            options=item.get('options', {})
                        )
                    )

                final_price = total_price + restaurant.delivery_tip

                # 1. Order 객체 생성
                order = Order.objects.create(
                    user=request.user,
                    restaurant=restaurant,
                    address=user_address,
                    total_price=total_price,
                    delivery_tip=restaurant.delivery_tip,
                    final_price=final_price,
                )

                # 2. OrderItem 객체들에 order 정보 할당 후 bulk_create로 한번에 생성
                for item in order_items_to_create:
                    item.order = order
                OrderItem.objects.bulk_create(order_items_to_create)

            # 성공 시, 주문 상세 페이지 URL을 반환
            order_detail_url = reverse_lazy('restaurants:order_detail', kwargs={'pk': order.pk})
            return JsonResponse({'success': True, 'redirect_url': order_detail_url})

        except Exception as e:
            # 서버 오류 발생 시
            return JsonResponse({'error': str(e)}, status=500)


class UserOrderListView(LoginRequiredMixin, ListView):
    """
    로그인한 사용자의 주문 내역 목록
    """
    model = Order
    template_name = 'restaurants/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # 현재 로그인한 사용자의 주문만 필터링하여 반환
        return Order.objects.filter(user=self.request.user).select_related('restaurant').prefetch_related('items__menu')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    특정 주문의 상세 내역
    """
    model = Order
    template_name = 'restaurants/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        # 현재 로그인한 사용자의 주문만 볼 수 있도록 쿼리셋 제한
        return Order.objects.filter(user=self.request.user)
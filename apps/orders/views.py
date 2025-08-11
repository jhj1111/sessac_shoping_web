from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse # Import JsonResponse
from django.views.decorators.csrf import csrf_exempt # For AJAX POST without CSRF token (for testing, not recommended for production)
from django.utils.decorators import method_decorator # To apply csrf_exempt to CBV

from .models import Cart, Order
from .services import CartService, OrderService

from ..restaurants.models import Menu

class CartView(LoginRequiredMixin, View):
    """
    장바구니 조회(GET) 및 아이템 추가(POST) 처리
    """
    template_name = 'orders/cart_detail.html'

    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        context = {'cart': cart}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        menu_id = request.POST.get('menu_id')
        quantity = int(request.POST.get('quantity', 1))
        options = {} # request.POST.get('options')
        
        menu = get_object_or_404(Menu, id=menu_id)
        cart.add_item(menu=menu, quantity=quantity, options=options)
        return redirect('orders:cart_view')


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    장바구니 기반 주문 생성(GET, POST)
    """
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['address', 'special_requests', 'payment_method'] # 예시 필드
    success_url = reverse_lazy('orders:order_complete') # 주문 완료 페이지로 이동

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


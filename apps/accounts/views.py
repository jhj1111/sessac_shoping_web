from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import RegisterForm
from django.contrib.auth.views import LogoutView

from .models import CustomUser, Address


from ..orders.models import Order
# from ..reviews.models import Review
# from ..favorites.models import Favorite
# from ..support.models import Inquiry

# --- 회원 관리 Views ---
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')
    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')

def home(request):
    return render(request, 'accounts/home.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')



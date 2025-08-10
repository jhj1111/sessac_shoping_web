from django.contrib import admin
from .models import Menu, MenuOption, Restaurant

# Register your models here.
admin.site.register(Menu)
admin.site.register(MenuOption)
admin.site.register(Restaurant)
from django.shortcuts import render, get_object_or_404
from .models import Restaurant, MenuCategory, Review

def restaurant_detail(request, restaurant_id):

    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    menu_categories = restaurant.menu_categories.all().prefetch_related('menus__option_groups__options')
    reviews = restaurant.reviews.all()

    context = {
        'restaurants': restaurant,
        'menu_categories': menu_categories,
        'reviews': reviews,
    }

    return render(request, 'restaurants/detail.html', context)
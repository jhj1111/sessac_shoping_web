from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    category = models.CharField(max_length=50)
    operating_hours = models.JSONField()
    minimum_order = models.PositiveIntegerField()
    delivery_fee = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)
    is_open = models.BooleanField(default=True)
    owner_notice = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def calculate_distance(self, user_lat, user_lon):
        # Placeholder for distance calculation logic
        pass

    def is_currently_open(self):
        # Placeholder for checking opening hours
        pass

    def update_rating(self):
        # Placeholder for rating update logic
        pass

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='restaurants/menu_images/', blank=True, null=True)
    category = models.CharField(max_length=50)
    is_popular = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.restaurant.name}] {self.name}'

    def get_formatted_price(self):
        # Placeholder for price formatting
        return f'{self.price}원'

    def toggle_availability(self):
        self.is_available = not self.is_available
        self.save()

class MenuOption(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # e.g., 'radio', 'checkbox'
    additional_price = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)
    choices = models.JSONField() # e.g., [{"name": "Option 1", "price": 0}, {"name": "Option 2", "price": 500}]

    def __str__(self):
        return f'{self.menu.name} - {self.name}'

    def get_choices_list(self):
        # Placeholder for returning choices as a list
        return self.choices

    def calculate_price(self, selected_choices):
        # Placeholder for price calculation based on selected options
        pass

class Post(models.Model):
        pass
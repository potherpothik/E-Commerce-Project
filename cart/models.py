from django.db import models
from django.conf import settings  # Add this import
from products.models import Product
import json

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    _variant_data = models.TextField(blank=True, null=True, db_column='variant_data')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.product.get_price() * self.quantity
    
    @property
    def variant_data(self):
        if self._variant_data:
            return json.loads(self._variant_data)
        return {}
    
    @variant_data.setter
    def variant_data(self, value):
        self._variant_data = json.dumps(value)

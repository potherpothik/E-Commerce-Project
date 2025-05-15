from django.db import models

from users.models import CustomUser
from products.models import Product, TimeStampedModel


class Payment(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)


class Order(TimeStampedModel):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    order_number = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    postcode = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default="New")
    is_ordered = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"


class OrderProduct(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path("place_order/", views.place_order, name="place_order"),
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path("payment_complete/", views.payment_complete, name="payment_complete"),
    path("order_complete/", views.order_complete, name="order_complete"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("order_status/<str:order_number>/", views.payment_status, name="order_status"),
    
    # SSLCommerz specific URLs
    path("sslc/success/", views.sslc_success, name="sslc_success"),
    path("sslc/fail/", views.sslc_fail, name="sslc_fail"),
    path("sslc/cancel/", views.sslc_cancel, name="sslc_cancel"),
    path("sslc/ipn/", views.sslc_ipn, name="sslc_ipn"),
    
    # Test endpoint for development
    path("test-sslcommerz/", views.test_sslcommerz, name="test_sslcommerz"),
]

# SSLCommerz Payment Gateway Integration Guide

## Overview
This guide provides instructions for integrating the SSLCommerz payment gateway into the Django e-commerce application. SSLCommerz is a popular payment processor in Bangladesh that allows for various payment methods.

## Prerequisites
1. SSLCommerz merchant account (sandbox for testing, live for production)
2. Store ID and Store Password from SSLCommerz
3. Django e-commerce application with order processing functionality

## Installation

Install the required package:
```bash
pip install sslcommerz-python
```

Add it to your requirements.txt:
```
sslcommerz-python==0.0.3
```

## Configuration

### 1. Add SSLCommerz settings to your settings.py

```python
# SSLCommerz Settings
SSLC_STORE_ID = 'your_store_id'  # Replace with your Store ID
SSLC_STORE_PASSWORD = 'your_store_password'  # Replace with your Store Password
SSLC_IS_SANDBOX = True  # True for testing, False for production
SSLC_CURRENCY = 'BDT'
SSLC_SUCCESS_URL = 'orders:sslc_success'
SSLC_FAIL_URL = 'orders:sslc_fail'
SSLC_CANCEL_URL = 'orders:sslc_cancel'
SSLC_IPN_URL = 'orders:sslc_ipn'
DOMAIN_NAME = 'http://yourdomain.com'  # Replace with your domain
```

For security, it's better to use environment variables:

```python
SSLC_STORE_ID = env('SSLC_STORE_ID')
SSLC_STORE_PASSWORD = env('SSLC_STORE_PASSWORD')
```

### 2. Create SSLCommerz utility module

Create a new file called `utils/sslcommerz.py`:

```python
from sslcommerz_python.payment import SSLCSession
from django.conf import settings
from django.urls import reverse
import uuid

def initiate_payment(request, order):
    """
    Initiates the SSLCommerz payment process
    
    Args:
        request: The HTTP request object
        order: The Order model instance
        
    Returns:
        The gateway URL for redirection or None if failed
    """
    # Create a unique transaction ID
    tran_id = f"{order.order_number}_{uuid.uuid4().hex[:6]}"
    
    # Save transaction ID to later verify the transaction
    order.payment_id = tran_id
    order.save()
    
    # Initialize SSLCommerz session
    sslcz = SSLCSession(
        sslc_is_sandbox=settings.SSLC_IS_SANDBOX,
        sslc_store_id=settings.SSLC_STORE_ID,
        sslc_store_passwd=settings.SSLC_STORE_PASSWORD
    )
    
    # Set the URLs
    domain = settings.DOMAIN_NAME
    sslcz.set_urls(
        success_url=f"{domain}{reverse(settings.SSLC_SUCCESS_URL)}",
        fail_url=f"{domain}{reverse(settings.SSLC_FAIL_URL)}",
        cancel_url=f"{domain}{reverse(settings.SSLC_CANCEL_URL)}",
        ipn_url=f"{domain}{reverse(settings.SSLC_IPN_URL)}"
    )
    
    # Set order details
    sslcz.set_product_integration(
        total_amount=order.order_total,
        currency=settings.SSLC_CURRENCY,
        product_category="Mixed",
        product_name=f"Order {order.order_number}",
        num_of_item=order.items.count(),
        shipping_method="Courier",
        product_profile="general"
    )
    
    # Set customer info
    sslcz.set_customer_info(
        name=request.user.get_full_name(),
        email=order.email,
        address1=order.address_line_1,
        address2=order.address_line_2,
        city=order.city,
        postcode=order.postcode,
        country=order.country,
        phone=order.mobile
    )
    
    # Set shipping info
    sslcz.set_shipping_info(
        shipping_to=request.user.get_full_name(),
        address=f"{order.address_line_1}, {order.address_line_2}",
        city=order.city,
        postcode=order.postcode,
        country=order.country
    )
    
    # Create SSLCommerz payment session
    response = sslcz.init_payment()
    
    # Return the payment gateway URL
    if response['status'] == 'SUCCESS':
        return response['GatewayPageURL']
    
    return None
```

### 3. Update Order Model

Add a field to store the payment transaction ID:

```python
class Order(TimeStampedModel):
    # Existing fields...
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    # Other fields...
```

### 4. Update views.py in the orders app

#### Payment Initiation View

```python
@login_required(login_url='users:login')
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Initiate SSLCommerz payment
        from utils.sslcommerz import initiate_payment
        
        payment_url = initiate_payment(request, order)
        
        if payment_url:
            return redirect(payment_url)
        else:
            messages.error(request, 'Payment gateway error. Please try again later.')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/payment.html', context)
```

#### SSLCommerz Callback Views

```python
@csrf_exempt
def sslc_success(request):
    """
    SSLCommerz payment success callback handler
    """
    if request.method == 'POST':
        payment_data = request.POST
        tran_id = payment_data.get('tran_id', '')
        status = payment_data.get('status', '')
        
        try:
            # Parse the transaction ID to get the order number
            order_number = tran_id.split('_')[0]
            order = Order.objects.get(order_number=order_number)
            
            # Create payment record
            payment = Payment(
                user=order.user,
                payment_id=tran_id,
                payment_method='SSLCommerz',
                amount_paid=payment_data.get('amount'),
                status='Completed'
            )
            payment.save()
            
            # Update order
            order.payment = payment
            order.is_ordered = True
            order.status = 'Accepted'
            order.save()
            
            # Create order products and reduce stock
            cart_items = CartItem.objects.filter(user=order.user)
            for item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    payment=payment,
                    user=order.user,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    ordered=True
                )
                
                # Reduce stock
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            # Clear cart
            cart_items.delete()
            
            # Send order confirmation email
            try:
                mail_subject = 'Thank you for your order!'
                message = render_to_string('orders/order_received_email.html', {
                    'user': order.user,
                    'order': order,
                })
                to_email = order.user.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            # Redirect to order complete page
            return redirect('orders:order_complete', order_number=order.order_number, payment_id=payment.payment_id)
            
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('orders:checkout')
    
    return redirect('home')
```

Add similar views for `sslc_fail`, `sslc_cancel`, and `sslc_ipn` as shown in the orders/views.py file you already have.

### 5. Update URLs in orders/urls.py

```python
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('my_orders/', views.my_orders, name='my_orders'),
    
    # SSLCommerz callback URLs
    path('sslc/success/', views.sslc_success, name='sslc_success'),
    path('sslc/fail/', views.sslc_fail, name='sslc_fail'),
    path('sslc/cancel/', views.sslc_cancel, name='sslc_cancel'),
    path('sslc/ipn/', views.sslc_ipn, name='sslc_ipn'),
]
```

## Payment Flow

1. User places an order
2. System redirects to the payment page
3. User selects SSLCommerz payment
4. System initiates SSLCommerz payment session
5. User is redirected to SSLCommerz payment gateway
6. User completes payment
7. SSLCommerz redirects back to your site (success, fail, or cancel URL)
8. System processes the callback and updates order status
9. User sees order confirmation

## Testing

1. Use the SSLCommerz sandbox environment for testing
2. Test with different payment methods
3. Test success, failure, and cancellation scenarios
4. Verify order status updates correctly
5. Ensure inventory is updated after successful payment
6. Check order confirmation emails are sent

## Going to Production

When ready to go live:

1. Change SSLCommerz sandbox mode to production:
```python
SSLC_IS_SANDBOX = False
```

2. Update your store ID and password with production credentials
3. Make sure your domain is properly configured with SSLCommerz
4. Implement thorough error handling and logging
5. Set up monitoring for payment callbacks

## Security Considerations

1. Always validate payment data from SSLCommerz
2. Use HTTPS for all payment-related pages
3. Implement IP whitelisting for IPN if possible
4. Store sensitive payment information securely
5. Implement transaction logging for auditing

## Troubleshooting

1. Check SSLCommerz API documentation for error codes
2. Review transaction logs in your SSLCommerz merchant dashboard
3. Verify callback URLs are correctly configured
4. Check for CSRF issues with exempt views
5. Test with different browsers and devices 
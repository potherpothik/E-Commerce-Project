import datetime
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages  # Add this import
from cart.models import CartItem
from .models import Order, OrderProduct, Payment
import uuid
from django.urls import reverse
from django.conf import settings

def generate_order_number():
    return str(uuid.uuid4()).split('-')[0].upper()

@login_required(login_url='users:login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('products:product_list')
    
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    
    if request.method == 'POST':
        # Create a new order
        order = Order()
        order.user = current_user
        order.mobile = request.POST.get('mobile')
        order.email = request.POST.get('email')
        order.address_line_1 = request.POST.get('address_line_1')
        order.address_line_2 = request.POST.get('address_line_2', '')
        order.country = request.POST.get('country')
        order.postcode = request.POST.get('postcode')
        order.city = request.POST.get('city')
        order.order_note = request.POST.get('order_note', '')
        order.order_total = total
        order.order_number = generate_order_number()
        order.save()
        
        # Redirect to payment page
        return redirect('orders:payment', order_id=order.id)
    
    return render(request, 'orders/checkout.html')

@login_required(login_url='users:login')
def payment(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    
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

@csrf_exempt
def payment_complete(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        order_id = body['order_id']
        payment_id = body['payment_id']
        payment_method = body['payment_method']
        
        # Get the order
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create payment
        payment = Payment(
            user=request.user,
            payment_id=payment_id,
            payment_method=payment_method,
            amount_paid=order.order_total,
            status='Completed'
        )
        payment.save()
        
        # Update order
        order.payment = payment
        order.is_ordered = True
        order.status = 'Accepted'
        order.save()
        
        # Create order products
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment
            order_product.user = request.user
            order_product.product = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()
            
            # Reduce product quantity
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        # Clear cart
        CartItem.objects.filter(user=request.user).delete()
        
        # Send order confirmation email
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_received_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        
        data = {
            'order_number': order.order_number,
            'payment_id': payment.payment_id,
        }
        return JsonResponse(data)
    
    return JsonResponse({'status': 'Failed'})

@login_required(login_url='users:login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order)
        payment = Payment.objects.get(payment_id=payment_id)
        
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'payment': payment,
        }
        return render(request, 'orders/order-success.html', context)
    
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('products:home')

@login_required(login_url='users:login')
def payment_status(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        payment = order.payment
        context = {
            'order': order,
            'payment': payment,
        }
        return render(request, 'orders/payment_status.html', context)
    
    except Order.DoesNotExist:
        return redirect('products:home')

@login_required(login_url='users:login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/my_orders.html', context)

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
            # Find the order with the transaction ID
            order = Order.objects.get(transaction_id=tran_id)
            
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

@csrf_exempt
def sslc_fail(request):
    """
    SSLCommerz payment failure callback handler
    """
    if request.method == 'POST':
        payment_data = request.POST
        messages.error(request, 'Payment failed. Please try again.')
    
    return redirect('products:home')

@csrf_exempt
def sslc_cancel(request):
    """
    SSLCommerz payment cancel callback handler
    """
    if request.method == 'POST':
        payment_data = request.POST
        messages.warning(request, 'Payment was cancelled.')
    
    return redirect('products:home')

@csrf_exempt
def sslc_ipn(request):
    """
    SSLCommerz payment IPN (Instant Payment Notification) handler
    """
    if request.method == 'POST':
        payment_data = request.POST
        
        # Process the IPN data (you might want to save this to a log)
        # This is called by SSLCommerz when a payment status changes
        
        tran_id = payment_data.get('tran_id', '')
        status = payment_data.get('status', '')
        
        try:
            # Find the order with the transaction ID
            order = Order.objects.get(transaction_id=tran_id)
            
            # Update order status based on payment status
            if status == 'VALID':
                # Payment is valid, mark order as paid
                if not order.is_ordered:
                    # Create payment record if it doesn't exist
                    payment, created = Payment.objects.get_or_create(
                        user=order.user,
                        payment_id=tran_id,
                        defaults={
                            'payment_method': 'SSLCommerz',
                            'amount_paid': payment_data.get('amount'),
                            'status': 'Completed'
                        }
                    )
                    
                    # Update order
                    order.payment = payment
                    order.is_ordered = True
                    order.status = 'Accepted'
                    order.save()
            
            elif status == 'FAILED':
                # Payment failed, update order status
                order.status = 'Cancelled'
                order.save()
            
            # Return a 200 OK response to SSLCommerz
            return HttpResponse("IPN received", status=200)
            
        except Order.DoesNotExist:
            # Order not found, still return a 200 OK to acknowledge receipt
            return HttpResponse("Order not found", status=200)
    
    # Redirect to home if accessed directly
    return redirect('products:home')

def test_sslcommerz(request):
    """
    Test endpoint for SSLCommerz integration
    This is for development purposes only
    """
    if not settings.DEBUG:
        return HttpResponse("This endpoint is only available in debug mode")
    
    # Check SSLCommerz configuration
    is_configured = (
        hasattr(settings, 'SSLC_STORE_ID') and 
        hasattr(settings, 'SSLC_STORE_PASSWORD') and
        hasattr(settings, 'SSLC_IS_SANDBOX') and
        hasattr(settings, 'SSLC_SUCCESS_URL') and
        hasattr(settings, 'SSLC_FAIL_URL') and
        hasattr(settings, 'SSLC_CANCEL_URL') and
        hasattr(settings, 'SSLC_IPN_URL')
    )
    
    # Get the domain name
    domain = settings.DOMAIN_NAME if hasattr(settings, 'DOMAIN_NAME') else settings.DOMAIN
    
    # Get the callback URLs
    success_url = f"{domain}{reverse(settings.SSLC_SUCCESS_URL)}" if hasattr(settings, 'SSLC_SUCCESS_URL') else "Not configured"
    fail_url = f"{domain}{reverse(settings.SSLC_FAIL_URL)}" if hasattr(settings, 'SSLC_FAIL_URL') else "Not configured"
    cancel_url = f"{domain}{reverse(settings.SSLC_CANCEL_URL)}" if hasattr(settings, 'SSLC_CANCEL_URL') else "Not configured"
    ipn_url = f"{domain}{reverse(settings.SSLC_IPN_URL)}" if hasattr(settings, 'SSLC_IPN_URL') else "Not configured"
    
    # Prepare the response
    if request.user.is_staff:
        response_data = {
            'is_configured': is_configured,
            'store_id': settings.SSLC_STORE_ID if hasattr(settings, 'SSLC_STORE_ID') else "Not configured",
            'store_password': '*******' if hasattr(settings, 'SSLC_STORE_PASSWORD') else "Not configured",
            'is_sandbox': settings.SSLC_IS_SANDBOX if hasattr(settings, 'SSLC_IS_SANDBOX') else "Not configured",
            'domain': domain,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'ipn_url': ipn_url,
        }
    else:
        response_data = {
            'is_configured': is_configured,
            'domain': domain,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'ipn_url': ipn_url,
        }
    
    # Return the response as JSON
    return JsonResponse(response_data)

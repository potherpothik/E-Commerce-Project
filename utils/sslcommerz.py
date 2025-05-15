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
    order.transaction_id = tran_id
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
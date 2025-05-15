from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category, Brand, Tag, ProductVariant, Review
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Wishlist

def home(request):
    # Get featured products or other products to display on homepage
    featured_products = Product.objects.filter(is_featured=True, slug__isnull=False).exclude(slug='')
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'products/index.html', context)
def about(request):
    return render(request, 'products/about.html')

def contact(request):
    return render(request, 'products/contact.html')

def products(request):
    products = Product.objects.filter(slug__isnull=False).exclude(slug='')
    return render(request, 'products/products.html', {'products': products})

def single_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/single-product.html', {'product': product})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popularity':
        products = products.order_by('-review_count')
    elif sort_by == 'rating':
        products = products.order_by('-average_rating')
    
    # Filtering
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    brand_slug = request.GET.get('brand')
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(sku__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_sorting': sort_by,
        'current_category': category_slug,
        'current_brand': brand_slug,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'search_query': query,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.filter(is_active=True)
    images = product.images.all()
    reviews = product.reviews.filter(status='approved').order_by('-created_at')
    related_products = Product.objects.filter(
        Q(category=product.category) | Q(tags__in=product.tags.all())
    ).exclude(id=product.id).distinct()[:4]
    
    # Get variant types and values for this product
    variant_types = variants.values_list('variant_type', flat=True).distinct()
    variant_values = {}
    for v_type in variant_types:
        variant_values[v_type] = variants.filter(variant_type=v_type).values_list('value', flat=True).distinct()
    
    context = {
        'product': product,
        'variants': variants,
        'images': images,
        'reviews': reviews,
        'related_products': related_products,
        'variant_types': variant_types,
        'variant_values': variant_values,
    }
    
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(sku__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    context = {
        'products': products,
        'search_query': query
    }
    
    return render(request, 'products/search_results.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'products': products,
    }
    
    return render(request, 'products/category_detail.html', context)

def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'brand': brand,
        'products': products,
    }
    
    return render(request, 'products/brand_detail.html', context)

def tag_products(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    products = Product.objects.filter(tags=tag, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'tag': tag,
        'products': products,
    }
    
    return render(request, 'products/tag_products.html', context)


# Add these view functions to your views.py file
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is already in wishlist
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        # If already in wishlist, remove it
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed from your wishlist.")
    else:
        # Add to wishlist
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.name} added to your wishlist.")
    
    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

@login_required
def view_wishlist(request):
    """View function to display the wishlist contents."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'products/wishlist.html', context)

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.conf import settings
import uuid
from decimal import Decimal

User = get_user_model()

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-managed "created_at" and
    "updated_at" fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True)  # Add SKU field
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        related_name='products'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)  # Add brand field
    tags = models.ManyToManyField('Tag', blank=True)  # Add tags field
    low_stock_threshold = models.PositiveIntegerField(default=5)  # For low stock alerts
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def update_average_rating(self):
        """Update the product's average rating and review count"""
        reviews = self.reviews.all()
        if reviews.exists():
            self.average_rating = sum(review.rating for review in reviews) / reviews.count()
            self.review_count = reviews.count()
        else:
            self.average_rating = 0
            self.review_count = 0
        self.save(update_fields=['average_rating', 'review_count'])

    def get_rating_percentage(self):
        """Get the percentage of each rating (1-5 stars)"""
        total_reviews = self.review_count
        if total_reviews == 0:
            return {i: 0 for i in range(1, 6)}
        
        rating_counts = {i: 0 for i in range(1, 6)}
        for review in self.reviews.all():
            rating_counts[review.rating] += 1
        
        return {rating: (count / total_reviews) * 100 for rating, count in rating_counts.items()}

    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.stock <= self.low_stock_threshold

class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

class ProductVariant(TimeStampedModel):
    VARIANT_TYPE_CHOICES = (
        ('color', 'Color'),
        ('size', 'Size'),
        ('material', 'Material'),
        ('style', 'Style'),
        ('other', 'Other'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_type = models.CharField(max_length=20, choices=VARIANT_TYPE_CHOICES, default='other')  # Add variant type
    name = models.CharField(max_length=100)  # e.g., "Color", "Size"
    value = models.CharField(max_length=100)  # e.g., "Red", "XL"
    sku = models.CharField(max_length=50, unique=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)  # Add variant-specific image
    
    class Meta:
        unique_together = ['product', 'name', 'value']

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

    @property
    def current_price(self):
        return self.product.current_price + self.price_adjustment

class Review(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    helpful_votes = models.PositiveIntegerField(default=0)
    not_helpful_votes = models.PositiveIntegerField(default=0)
    moderator_notes = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='moderated_reviews'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product

    def __str__(self):
        return f"{self.user.username}'s review for {self.product.name}"

    def save(self, *args, **kwargs):
        # Update product's average rating
        super().save(*args, **kwargs)
        self.product.update_average_rating()

    @property
    def helpful_score(self):
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return (self.helpful_votes / total_votes) * 100

class ReviewResponse(TimeStampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_seller_response = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response to {self.review} by {self.user.username}"

class ReviewVote(TimeStampedModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']  # One vote per user per review

    def __str__(self):
        return f"{self.user.username} voted {'helpful' if self.is_helpful else 'not helpful'} for {self.review}"

    def save(self, *args, **kwargs):
        # Update review's helpful/not helpful counts
        if self.is_helpful:
            self.review.helpful_votes += 1
        else:
            self.review.not_helpful_votes += 1
        self.review.save()
        super().save(*args, **kwargs)

class ReviewReport(TimeStampedModel):
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake Review'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant to Product'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed')
    ]

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_reports'
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['review', 'reporter']  # One report per user per review

    def __str__(self):
        return f"Report on {self.review} by {self.reporter.username}"

class ReviewAnalytics(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='review_analytics')
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_distribution = models.JSONField(default=dict)  # Stores count of each rating
    helpful_votes_total = models.PositiveIntegerField(default=0)
    verified_purchase_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_analytics(self):
        reviews = self.product.reviews.filter(status='approved')
        self.total_reviews = reviews.count()
        
        if self.total_reviews > 0:
            self.average_rating = sum(review.rating for review in reviews) / self.total_reviews
            self.helpful_votes_total = sum(review.helpful_votes for review in reviews)
            verified_count = reviews.filter(is_verified_purchase=True).count()
            self.verified_purchase_percentage = (verified_count / self.total_reviews) * 100
            
            # Update rating distribution
            distribution = {i: 0 for i in range(1, 6)}
            for review in reviews:
                distribution[review.rating] += 1
            self.rating_distribution = distribution
        
        self.save()

    def __str__(self):
        return f"Analytics for {self.product.name}"

class CompareProduct(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compare_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compared_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Wishlist(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        
    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"

class Banner(TimeStampedModel):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

class Cart(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.quantity * self.product.price

class Order(TimeStampedModel):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
    ]

    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Shipping Information
    shipping_name = models.CharField(max_length=100)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    shipping_phone = models.CharField(max_length=20)
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Order Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_order_items')  # Added unique related_name
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

class Brand(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

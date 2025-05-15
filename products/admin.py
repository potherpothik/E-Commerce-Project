from django.contrib import admin
from .models import (
    Product, Category, ProductImage, ProductVariant, 
    Review, ReviewResponse, Brand, Tag
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'comment', 'created_at')
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'sale_price', 'stock', 'is_active', 'is_featured', 'average_rating')
    list_filter = ('is_active', 'is_featured', 'category', 'brand')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline, ReviewInline]
    list_editable = ('price', 'sale_price', 'stock', 'is_active', 'is_featured')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Categorization', {
            'fields': ('category', 'brand', 'tags')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'stock', 'low_stock_threshold')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'review_count')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_featured')
    list_filter = ('is_featured', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'status', 'created_at')
    list_filter = ('status', 'rating')
    search_fields = ('title', 'comment', 'user__email', 'product__name')
    readonly_fields = ('user', 'product', 'rating', 'title', 'comment', 'created_at')
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(status='approved')
    approve_reviews.short_description = "Mark selected reviews as approved"
    
    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
    reject_reviews.short_description = "Mark selected reviews as rejected"

admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(ReviewResponse)

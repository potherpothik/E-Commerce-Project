from django.core.management.base import BaseCommand
from products.models import Product
from django.utils.text import slugify
import uuid


class Command(BaseCommand):
    help = 'Fix products with missing or empty slugs'

    def handle(self, *args, **options):
        # Find products with empty or null slugs
        products_with_empty_slugs = Product.objects.filter(slug__isnull=True) | Product.objects.filter(slug='')
        count = products_with_empty_slugs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No products with empty slugs found.'))
            return
        
        self.stdout.write(f'Found {count} products with empty slugs. Fixing...')
        
        for product in products_with_empty_slugs:
            # Generate slug from product name
            base_slug = slugify(product.name)
            
            # Check if the slug already exists
            if Product.objects.filter(slug=base_slug).exists():
                # Append a UUID to make it unique
                base_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
            
            product.slug = base_slug
            product.save(update_fields=['slug'])
            
            self.stdout.write(f'Fixed slug for product "{product.name}": {product.slug}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {count} products with empty slugs.')) 
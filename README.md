# Django E-Commerce Project Documentation

## Project Overview
This is a modern, scalable, and secure e-commerce website built using the Django framework. The application allows users to browse products, register/login, add items to the cart, and complete purchases using the SSLCommerz payment gateway.

## Project Structure
The project is structured into several Django apps:

- **ecommerce** (Main project configuration)
- **products** (Product catalog, search, filtering, and reviews)
- **users** (Custom user model, authentication, profile management)
- **cart** (Shopping cart functionality)
- **orders** (Order processing, payment integration)

## Implemented Features

### 1. User Management & Authentication
- Custom User Model with additional fields (phone, profile picture, address)
- Email-based registration and login
- Password reset functionality
- Google OAuth integration
- User profile management
- Role-based access control

### 2. Product Catalog
- Comprehensive product model with variants, categories, tags, and brands
- Multiple product images
- Product reviews and ratings
- Search functionality with filtering by category, price, brand
- Sorting options (price, newest, popularity)
- Related products display
- Wishlist functionality

### 3. Shopping Cart
- Session-based cart for guests, DB-based for logged-in users
- Add/remove items, update quantities
- Display of subtotal, taxes, shipping, and total
- Cart persistence across sessions

### 4. Checkout & Orders
- Multi-step checkout process
- Order summary
- Order confirmation
- Order history in user dashboard

### 5. Payment Integration
- SSLCommerz payment gateway integration
- Payment status tracking
- Success/fail/cancel handlers

### 6. Frontend
- Responsive design using Bootstrap
- Home page with featured products and categories
- Product listing and detail pages
- Cart and checkout pages
- User dashboard

## Environment Setup
The project uses:
- Python environment management (venv)
- Environment variables for sensitive information (.env file)
- Django 4.x
- Key packages: allauth for authentication, Pillow for image processing

## Database Schema
The key models include:
- `CustomUser`: Extended user model with additional fields
- `Product`: Main product details with relationships to categories, brands
- `ProductVariant`: Different variations (size, color) of products
- `Category`: Product categorization with nesting support
- `Cart/CartItem`: Shopping cart implementation
- `Order/OrderProduct`: Order processing and line items
- `Payment`: Payment tracking and processing

## Deployment Considerations
- Currently configured for development environment
- For production, update settings for:
  - DEBUG mode
  - Database (PostgreSQL recommended)
  - Static file serving
  - Email configuration
  - SSLCommerz credentials

## Roadmap for Completion

### Short-term Improvements
1. Complete the SSLCommerz integration for production
2. Enhance the product filtering on the frontend
3. Add product stock management when orders are placed
4. Improve email notifications for orders and account actions

### Medium-term Features
1. Add admin dashboard with sales metrics
2. Implement discount codes/coupon system
3. Add product comparison functionality
4. Enhance SEO features (sitemaps, meta tags)

### Long-term Features
1. API endpoints for mobile app integration
2. Performance optimization (caching, query optimization)
3. Background task processing with Celery for emails and reports
4. Analytics and reporting dashboard

## Development Guidelines
1. Follow Django best practices for views and models
2. Keep the template structure consistent
3. Write tests for new functionality
4. Document any new features or changes
5. Use environment variables for sensitive information

## Required Environment Variables
```
SECRET_KEY=<django-secret-key>
EMAIL_HOST_USER=<email-for-notifications>
EMAIL_HOST_PASSWORD=<email-password>
```

## Running the Project
1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the environment: `source env/bin/activate` (Linux/Mac) or `env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables in a `.env` file
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the server: `python manage.py runserver`

## Contributing
1. Create a new branch for your feature
2. Write tests for your changes
3. Submit a pull request with a clear description # E-Commerce-Project

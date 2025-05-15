import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
if os.path.exists(BASE_DIR / '.env'):
    import environ
    env = environ.Env()
    environ.Env.read_env(BASE_DIR / '.env')
else:
    raise Exception("Could not find .env file")

SECRET_KEY = env('SECRET_KEY')
# 'django-insecure-l#!-q2-vv-bk**)42^e_rvr%2x3tov&k7@$k888@d)292zyept'

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',  # Replace with actual ID
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET', # Replace with actual secret
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'APP': {
            'client_id': 'YOUR_FACEBOOK_APP_ID',    # Replace with actual ID
            'secret': 'YOUR_FACEBOOK_APP_SECRET',   # Replace with actual secret
        },
        'SCOPE': ['email', 'public_profile'],
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': False
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
SERVER_EMAIL = env('EMAIL_HOST_USER')

# Allauth Configuration
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook', 
    'cart',
    'products.apps.ProductsConfig',
    'users.apps.UsersConfig',
    'orders',
]

AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Add this line
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Django AllAuth Settings
AUTHENTICATION_BACKENDS = [
    # Default Django backend
    'django.contrib.auth.backends.ModelBackend',
    
    # Django AllAuth backend
    'allauth.account.auth_backends.AuthenticationBackend',
    
    # Custom email backend
    'users.authentication.EmailBackend',
]

SITE_ID = 1
# Updated allauth configuration
ACCOUNT_LOGIN_METHODS = ['email']  # Replace ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_SIGNUP_FIELDS = ['email*']  # Add asterisk for mandatory field
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL = 'users.CustomUser'

# Remove deprecated settings
# ACCOUNT_AUTHENTICATION_METHOD 
# ACCOUNT_EMAIL_REQUIRED 
# ACCOUNT_LOGIN_METHODS

DOMAIN = 'http://localhost:8000'
# DOMAIN = 'http://localhost:8000/accounts/google/login/callback/'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEBUG = True

ALLOWED_HOSTS = ['*']  # Allow all hosts during development


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# SSLCommerz Settings
SSLC_STORE_ID = os.environ.get('SSLC_STORE_ID', 'your_store_id')
SSLC_STORE_PASSWORD = os.environ.get('SSLC_STORE_PASSWORD', 'your_store_password')
SSLC_IS_SANDBOX = True  # True for testing, False for production
SSLC_CURRENCY = 'BDT'
SSLC_SUCCESS_URL = 'orders:sslc_success'
SSLC_FAIL_URL = 'orders:sslc_fail'
SSLC_CANCEL_URL = 'orders:sslc_cancel'
SSLC_IPN_URL = 'orders:sslc_ipn'
DOMAIN_NAME = DOMAIN
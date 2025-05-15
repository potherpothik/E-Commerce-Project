from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('accounts/', include('allauth.urls')),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('privacy-settings/', views.privacy_settings, name='privacy_settings'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        success_url=reverse_lazy('users:password_reset_done')), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url=reverse_lazy('users:password_change_done')), name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
]
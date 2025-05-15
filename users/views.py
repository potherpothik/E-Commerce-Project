from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will be inactive until email verification
            user.save()
            
            # Send verification email
            send_verification_email(request, user)
            
            messages.success(request, 'Account created successfully. Please check your email to verify your account.')
            return redirect('products:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('products:home')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'users/login.html')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle form submission
        # Update user profile
        messages.success(request, 'Profile updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/edit_profile.html')

def otp_verification(request):
    if request.method == 'POST':
        # Verify OTP
        return redirect('products:home')
    return render(request, 'users/otp.html')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Logic to resend verification email
        messages.success(request, 'Verification email has been resent. Please check your inbox.')
        return redirect('users:login')
    return render(request, 'users/resend_verification.html')

@login_required
def privacy_settings(request):
    if request.method == 'POST':
        # Update privacy settings
        messages.success(request, 'Privacy settings updated successfully.')
        return redirect('users:profile')
    return render(request, 'users/privacy_settings.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        # Send account deletion email
        send_account_deletion_email(user)
        # Schedule account for deletion or delete immediately
        messages.success(request, 'Your account has been scheduled for deletion.')
        return redirect('products:home')
    return render(request, 'users/delete_account.html')

# Helper functions for email sending
def send_verification_email(request, user):
    """Send verification email to user"""
    verification_url = f"{request.scheme}://{request.get_host()}/users/verify/{user.id}/"
    context = {
        'user': user,
        'verification_url': verification_url
    }
    email_html = render_to_string('users/verification_email.html', context)
    send_mail(
        'Verify Your Email Address',
        'Please verify your email address',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def send_account_deletion_email(user):
    """Send account deletion notification email"""
    deletion_date = timezone.now() + timezone.timedelta(days=14)  # 14 days grace period
    context = {
        'user': user,
        'deletion_date': deletion_date
    }
    email_html = render_to_string('users/account_deletion_email.html', context)
    send_mail(
        'Account Deletion Request',
        'Your account is scheduled for deletion',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def send_password_change_notification(user):
    """Send password change notification email"""
    context = {
        'user': user,
        'change_time': timezone.now()
    }
    email_html = render_to_string('users/password_change_notification.html', context)
    send_mail(
        'Password Change Notification',
        'Your password has been changed',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=email_html,
        fail_silently=False,
    )

def user_login(request):
    # Function logic with the redirect at the end
    return redirect('products:home')  # Update this line

def user_register(request):
    # Function logic with the redirect at the end
    return redirect('products:home')  # Update this line

def password_reset_done(request):
    # Function logic with the redirect at the end
    return redirect('products:home')  # Update this line

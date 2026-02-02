"""
Services handle business logic that's too complex for views
Only create services when logic becomes complex or reusable
"""
import secrets
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import CustomUser, EmailVerificationToken


class EmailService:
    """
    Handles email operations
    Separated because: email logic is complex and reused across features
    """
    
    @staticmethod
    def send_verification_email(user, request):
        """Send email verification link to user"""
        # Generate token
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(user=user, token=token)
        
        # Build verification link
        current_site = get_current_site(request)
        verification_link = f"{request.scheme}://{current_site.domain}/api/auth/verify-email/{token}/"
        
        # Render email
        html_message = render_to_string('accounts/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
            'domain': current_site.domain,
        })
        
        # Send email
        send_mail(
            subject='Verify your email',
            message=f'Click this link to verify: {verification_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    @staticmethod
    def verify_token(token):
        """Verify email token and activate user"""
        try:
            verification = EmailVerificationToken.objects.select_related('user').get(token=token)
            
            if verification.is_expired():
                return None, "Token has expired"
            
            user = verification.user
            
            if user.is_verified:
                return user, "Email already verified"
            
            # Activate user
            user.is_verified = True
            user.is_active = True
            user.save()
            
            # Delete used token
            verification.delete()
            
            return user, "Email verified successfully"
            
        except EmailVerificationToken.DoesNotExist:
            return None, "Invalid token"


class AuthService:
    """
    Handles authentication business logic
    Separated because: auth workflows are complex and involve multiple steps
    """
    
    @staticmethod
    def register_user(email, password, first_name='', last_name='', request=None):
        """
        Register a new user and send verification email
        Returns: (user, error_message)
        """
        # Check if user exists
        if CustomUser.objects.filter(email=email).exists():
            return None, "Email already registered"
        
        # Create user
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as e:
            return None, str(e)
        
        # Send verification email
        try:
            EmailService.send_verification_email(user, request)
            return user, None
        except Exception as e:
            # Rollback: delete user if email fails
            user.delete()
            return None, f"Failed to send verification email: {str(e)}"
    
    @staticmethod
    def login_user(email, password):
        """
        Authenticate user and return tokens
        Returns: (tokens_dict, error_message)
        """
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None, "Invalid credentials"
        
        if not user.check_password(password):
            return None, "Invalid credentials"
        
        if not user.is_active:
            return None, "Account not activated. Please verify your email."
        
        if not user.is_verified:
            return None, "Email not verified. Please check your email."
        
        # Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, None
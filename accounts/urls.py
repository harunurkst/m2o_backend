from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    VerifyEmailView,
    ResendVerificationView,
    UserProfileView,
    ChangePasswordView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Email verification
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # User management
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # JWT token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
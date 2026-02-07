from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    VerifyEmailView,
    ResendVerificationView,
    UserProfileView,
    ChangePasswordView,
)
from .viewsets import OrganizationViewSet, BusinessViewSet

app_name = 'accounts'

# Router for ViewSets
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')

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
    
    # Multi-tenant API - Nested routes
    path(
        'organizations/<int:organization_id>/businesses/',
        BusinessViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='organization-businesses-list'
    ),
    path(
        'organizations/<int:organization_id>/businesses/<int:id>/',
        BusinessViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='organization-businesses-detail'
    )
]

# Add router URLs
urlpatterns += router.urls
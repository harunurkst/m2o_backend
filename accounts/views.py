from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    EmailSerializer,
)
from .services import AuthService, EmailService


class RegisterView(APIView):
    """User registration endpoint"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Register user via service
        user, error = AuthService.register_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            request=request
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            {
                'message': 'Registration successful. Please check your email to verify your account.',
                'email': user.email
            },
            status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):
    """Email verification endpoint"""
    
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        user, message = EmailService.verify_token(token)
        
        if user is None:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': message}, status=status.HTTP_200_OK)


class ResendVerificationView(APIView):
    """Resend verification email"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(email=email)
            
            if user.is_verified:
                return Response(
                    {'message': 'Email already verified'},
                    status=status.HTTP_200_OK
                )
            
            EmailService.send_verification_email(user, request)
            return Response(
                {'message': 'Verification email sent'},
                status=status.HTTP_200_OK
            )
            
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists (security)
            return Response(
                {'message': 'If email exists, verification link will be sent'},
                status=status.HTTP_200_OK
            )


class LoginView(APIView):
    """Login endpoint"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate via service
        tokens, error = AuthService.login_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout endpoint - blacklist refresh token"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    """Get and update user profile"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Verify old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password updated successfully'},
            status=status.HTTP_200_OK
        )
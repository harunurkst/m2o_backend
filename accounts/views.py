from rest_framework import status, serializers as drf_serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer

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
    
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name='RegisterResponse',
                fields={
                    'message': drf_serializers.CharField(),
                    'email': drf_serializers.EmailField(),
                }
            )
        },
        examples=[
            OpenApiExample(
                'Register Request',
                value={
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                    "password2": "SecurePass123!",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                request_only=True
            ),
            OpenApiExample(
                'Register Response',
                value={
                    "message": "Registration successful. Please check your email to verify your account.",
                    "email": "user@example.com"
                },
                response_only=True
            )
        ],
        tags=['Authentication']
    )
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
    
    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name='VerifyEmailResponse',
                fields={'message': drf_serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Verify Email Response',
                value={"message": "Email verified successfully"},
                response_only=True
            )
        ],
        tags=['Authentication']
    )
    def get(self, request, token):
        user, message = EmailService.verify_token(token)
        
        if user is None:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': message}, status=status.HTTP_200_OK)


class ResendVerificationView(APIView):
    """Resend verification email"""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=EmailSerializer,
        responses={
            200: inline_serializer(
                name='ResendVerificationResponse',
                fields={'message': drf_serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Resend Verification Request',
                value={"email": "user@example.com"},
                request_only=True
            ),
            OpenApiExample(
                'Resend Verification Response',
                value={"message": "Verification email sent"},
                response_only=True
            )
        ],
        tags=['Authentication']
    )
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
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'access': drf_serializers.CharField(),
                    'refresh': drf_serializers.CharField(),
                    'user': UserSerializer(),
                }
            )
        },
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    "email": "user@example.com",
                    "password": "SecurePass123!"
                },
                request_only=True
            ),
            OpenApiExample(
                'Login Response',
                value={
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_verified": True
                    }
                },
                response_only=True
            )
        ],
        tags=['Authentication']
    )
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
    
    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name='LogoutResponse',
                fields={'message': drf_serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Logout Response',
                value={"message": "Logged out successfully"},
                response_only=True
            )
        ],
        tags=['Authentication']
    )
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
    
    @extend_schema(
        responses={200: UserSerializer},
        tags=['Authentication']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['Authentication']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['Authentication']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: inline_serializer(
                name='ChangePasswordResponse',
                fields={'message': drf_serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Change Password Request',
                value={
                    "old_password": "OldPass123!",
                    "new_password": "NewPass123!",
                    "new_password2": "NewPass123!"
                },
                request_only=True
            ),
            OpenApiExample(
                'Change Password Response',
                value={"message": "Password updated successfully"},
                response_only=True
            )
        ],
        tags=['Authentication']
    )
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
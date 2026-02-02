from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'is_verified', 'date_joined']


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )


class EmailSerializer(serializers.Serializer):
    """Serializer for email operations"""
    
    email = serializers.EmailField(required=True)
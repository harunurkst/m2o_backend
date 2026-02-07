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


# ============================================================================
# Multi-Tenant Serializers
# ============================================================================

from .models import Organization, OrganizationMembership, Business


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for organization membership"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'user', 'user_email', 'user_name', 'organization',
            'role', 'joined_at', 'invited_by', 'invited_by_email'
        ]
        read_only_fields = ['id', 'joined_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing organizations"""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    member_count = serializers.SerializerMethodField()
    business_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'owner', 'owner_email',
            'is_active', 'created_at', 'updated_at',
            'member_count', 'business_count', 'user_role'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_business_count(self, obj):
        return obj.businesses.filter(is_active=True).count()
    
    def get_user_role(self, obj):
        """Get current user's role in this organization"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = OrganizationMembership.objects.filter(
                user=request.user,
                organization=obj
            ).first()
            return membership.role if membership else None
        return None


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for organization with nested data"""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    memberships = OrganizationMembershipSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    business_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'owner', 'owner_email',
            'is_active', 'created_at', 'updated_at',
            'memberships', 'member_count', 'business_count'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_business_count(self, obj):
        return obj.businesses.filter(is_active=True).count()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations"""
    
    class Meta:
        model = Organization
        fields = ['name', 'slug']
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Organization with this slug already exists.")
        return value
    
    def create(self, validated_data):
        """Create organization with current user as owner"""
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)


class BusinessSerializer(serializers.ModelSerializer):
    """Serializer for business"""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    integration_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = [
            'id', 'organization', 'organization_name', 'name', 'slug',
            'description', 'is_active', 'created_at', 'updated_at',
            'integration_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_integration_count(self, obj):
        return obj.integrations.filter(is_active=True).count()
    
    def validate(self, attrs):
        """Validate user has access to organization"""
        request = self.context.get('request')
        organization = attrs.get('organization')
        
        # Check if user is a member of the organization
        if not organization.members.filter(id=request.user.id).exists():
            raise serializers.ValidationError(
                "You don't have permission to create businesses in this organization."
            )
        
        return attrs


class BusinessCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating businesses"""
    
    class Meta:
        model = Business
        fields = ['name', 'slug', 'description']
    
    def validate_slug(self, value):
        """Ensure slug is unique within organization"""
        organization = self.context.get('organization')
        if Business.objects.filter(organization=organization, slug=value).exists():
            raise serializers.ValidationError(
                "Business with this slug already exists in this organization."
            )
        return value
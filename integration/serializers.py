from rest_framework import serializers
from .models import Platform, BusinessPlatform

class PlatformSerializer(serializers.ModelSerializer):
    """Serializer for the Platform model."""
    class Meta:
        model = Platform
        fields = [
            'id', 'uuid', 'name', 'description', 'description_fr',
            'parent', 'client_id', 'client_secret', 'scope',
            'authorize_url', 'redirect_url', 'token_url', 'logo_url',
            'tags', 'is_active', 'is_post'
        ]
        read_only_fields = ['id', 'uuid']

class BusinessPlatformSerializer(serializers.ModelSerializer):
    """Serializer for the BusinessPlatform model."""
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = BusinessPlatform
        fields = [
            'id', 'uuid', 'business', 'business_name', 'platform', 'platform_name',
            'access_token', 'refresh_token', 'access_token_secret', 'expire_at',
            'is_active', 'platform_type', 'reconnection', 'external_id',
            'external_name', 'external_profile_picture'
        ]
        read_only_fields = ['id', 'uuid', 'platform_name', 'business_name']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
            'access_token_secret': {'write_only': True},
        }

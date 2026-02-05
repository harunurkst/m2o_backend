from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    inline_serializer
)
from rest_framework import serializers as drf_serializers

from .models import Organization, OrganizationMembership, Business, Integration, FacebookPageIntegration
from .serializers import (
    OrganizationListSerializer,
    OrganizationDetailSerializer,
    OrganizationCreateSerializer,
    OrganizationMembershipSerializer,
    BusinessSerializer,
    BusinessCreateSerializer,
    IntegrationSerializer,
    FacebookPageIntegrationSerializer,
)
from .permissions import IsOrganizationMember, IsOrganizationAdmin, IsBusinessOwner


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organization management and onboarding.
    
    Provides endpoints for creating, listing, and managing organizations
    in a multi-tenant environment.
    """
    
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return organizations where user is a member"""
        return Organization.objects.filter(
            members=self.request.user,
            is_active=True
        ).distinct().select_related('owner').prefetch_related('memberships__user')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return OrganizationCreateSerializer
        elif self.action == 'list':
            return OrganizationListSerializer
        return OrganizationDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy', 'add_member', 'remove_member']:
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated()]
    
    @extend_schema(
        summary="Create organization",
        description="Create a new organization. The authenticated user becomes the owner and is automatically added as a member with OWNER role.",
        request=OrganizationCreateSerializer,
        responses={
            201: OrganizationDetailSerializer,
            400: OpenApiResponse(description="Validation error")
        },
        examples=[
            OpenApiExample(
                'Create Organization Request',
                value={
                    "name": "My Company",
                    "slug": "my-company"
                },
                request_only=True
            ),
            OpenApiExample(
                'Create Organization Response',
                value={
                    "id": 1,
                    "name": "My Company",
                    "slug": "my-company",
                    "owner": 1,
                    "owner_email": "user@example.com",
                    "is_active": True,
                    "created_at": "2026-02-05T12:00:00Z",
                    "updated_at": "2026-02-05T12:00:00Z",
                    "memberships": [
                        {
                            "id": 1,
                            "user": 1,
                            "user_email": "user@example.com",
                            "user_name": "John Doe",
                            "organization": 1,
                            "role": "OWNER",
                            "joined_at": "2026-02-05T12:00:00Z",
                            "invited_by": None,
                            "invited_by_email": None
                        }
                    ],
                    "member_count": 1,
                    "business_count": 0
                },
                response_only=True,
                status_codes=['201']
            )
        ],
        tags=['Organizations']
    )
    def create(self, request, *args, **kwargs):
        """Create organization - Onboarding endpoint"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.save()
        
        # Return detailed organization data
        detail_serializer = OrganizationDetailSerializer(
            organization,
            context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="List user's organizations",
        description="Get all organizations where the authenticated user is a member.",
        responses={200: OrganizationListSerializer(many=True)},
        examples=[
            OpenApiExample(
                'List Organizations Response',
                value=[
                    {
                        "id": 1,
                        "name": "My Company",
                        "slug": "my-company",
                        "owner": 1,
                        "owner_email": "owner@example.com",
                        "is_active": True,
                        "created_at": "2026-02-05T12:00:00Z",
                        "updated_at": "2026-02-05T12:00:00Z",
                        "member_count": 3,
                        "business_count": 2,
                        "user_role": "OWNER"
                    }
                ],
                response_only=True
            )
        ],
        tags=['Organizations']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get organization details",
        description="Get detailed information about a specific organization including members and businesses.",
        responses={200: OrganizationDetailSerializer},
        tags=['Organizations']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        """Soft delete organization"""
        instance.is_active = False
        instance.save()
    
    @extend_schema(
        summary="Add member to organization",
        description="Add a new member to the organization. Requires ADMIN or OWNER role.",
        request=OrganizationMembershipSerializer,
        responses={201: OrganizationMembershipSerializer},
        examples=[
            OpenApiExample(
                'Add Member Request',
                value={
                    "user": 2,
                    "role": "ADMIN"
                },
                request_only=True
            ),
            OpenApiExample(
                'Add Member Response',
                value={
                    "id": 2,
                    "user": 2,
                    "user_email": "newmember@example.com",
                    "user_name": "Jane Doe",
                    "organization": 1,
                    "role": "ADMIN",
                    "joined_at": "2026-02-05T14:00:00Z",
                    "invited_by": 1,
                    "invited_by_email": "owner@example.com"
                },
                response_only=True
            )
        ],
        tags=['Organizations']
    )
    @action(detail=True, methods=['post'])
    def add_member(self, request, id=None):
        """Add a member to the organization"""
        organization = self.get_object()
        serializer = OrganizationMembershipSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set organization and invited_by
        membership = serializer.save(
            organization=organization,
            invited_by=request.user
        )
        
        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Remove member from organization",
        description="Remove a member from the organization. Requires ADMIN or OWNER role. Cannot remove the organization owner.",
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description='ID of the user to remove',
                required=True
            )
        ],
        responses={
            204: None,
            400: OpenApiResponse(description="Cannot remove owner or validation error"),
            404: OpenApiResponse(description="User not found in organization")
        },
        tags=['Organizations']
    )
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, id=None):
        """Remove a member from the organization"""
        organization = self.get_object()
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing the owner
        if int(user_id) == organization.owner.id:
            return Response(
                {'error': 'Cannot remove the organization owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove membership
        deleted_count, _ = OrganizationMembership.objects.filter(
            organization=organization,
            user_id=user_id
        ).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'User is not a member of this organization'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Business CRUD operations.
    
    Endpoints:
    - GET /api/organizations/{org_id}/businesses/ - List businesses in organization
    - POST /api/organizations/{org_id}/businesses/ - Create new business (onboarding)
    - GET /api/organizations/{org_id}/businesses/{id}/ - Get business details
    - PUT/PATCH /api/organizations/{org_id}/businesses/{id}/ - Update business
    - DELETE /api/organizations/{org_id}/businesses/{id}/ - Soft delete business
    """
    
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsBusinessOwner]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return businesses in the organization"""
        org_id = self.kwargs.get('organization_id')
        return Business.objects.filter(
            organization_id=org_id,
            organization__members=self.request.user,
            is_active=True
        ).select_related('organization')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BusinessCreateSerializer
        return BusinessSerializer
    
    @extend_schema(
        summary="Create business",
        description="Create a new business within an organization. User must be a member of the organization.",
        request=BusinessCreateSerializer,
        responses={
            201: BusinessSerializer,
            404: OpenApiResponse(description="Organization not found or access denied")
        },
        examples=[
            OpenApiExample(
                'Create Business Request',
                value={
                    "name": "E-commerce Store",
                    "slug": "ecommerce-store",
                    "description": "Our main online store"
                },
                request_only=True
            ),
            OpenApiExample(
                'Create Business Response',
                value={
                    "id": 1,
                    "organization": 1,
                    "organization_name": "My Company",
                    "name": "E-commerce Store",
                    "slug": "ecommerce-store",
                    "description": "Our main online store",
                    "is_active": True,
                    "created_at": "2026-02-05T12:00:00Z",
                    "updated_at": "2026-02-05T12:00:00Z",
                    "integration_count": 0
                },
                response_only=True
            )
        ],
        tags=['Businesses']
    )
    def create(self, request, organization_id=None):
        """Create business - Onboarding endpoint"""
        # Get organization and verify access
        try:
            organization = Organization.objects.get(
                id=organization_id,
                members=request.user,
                is_active=True
            )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found or you do not have access'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'organization': organization}
        )
        serializer.is_valid(raise_exception=True)
        business = serializer.save(organization=organization)
        
        # Return detailed business data
        detail_serializer = BusinessSerializer(business, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="List businesses in organization",
        description="Get all active businesses in the specified organization.",
        responses={200: BusinessSerializer(many=True)},
        examples=[
            OpenApiExample(
                'List Businesses Response',
                value=[
                    {
                        "id": 1,
                        "organization": 1,
                        "organization_name": "My Company",
                        "name": "E-commerce Store",
                        "slug": "ecommerce-store",
                        "description": "Our main online store",
                        "is_active": True,
                        "created_at": "2026-02-05T12:00:00Z",
                        "updated_at": "2026-02-05T12:00:00Z",
                        "integration_count": 2
                    }
                ],
                response_only=True
            )
        ],
        tags=['Businesses']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        """Soft delete business"""
        instance.is_active = False
        instance.save()


class IntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Integration management.
    
    Provides endpoints for creating and managing integrations
    (Facebook, WhatsApp, Slack) for businesses.
    """
    
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return integrations for the business"""
        business_id = self.kwargs.get('business_id')
        return Integration.objects.filter(
            business_id=business_id,
            business__organization__members=self.request.user,
            is_active=True
        ).select_related('business', 'business__organization')
    
    @extend_schema(
        summary="Create integration",
        description="Create a new integration for a business. Supports Facebook Page, WhatsApp, and Slack integrations.",
        request=IntegrationSerializer,
        responses={
            201: IntegrationSerializer,
            400: OpenApiResponse(description="Validation error")
        },
        examples=[
            OpenApiExample(
                'Create Facebook Integration Request',
                value={
                    "integration_type": "FACEBOOK_PAGE",
                    "name": "Main Facebook Page",
                    "config": {
                        "auto_reply": True,
                        "webhook_enabled": True
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Create Integration Response',
                value={
                    "id": 1,
                    "business": 1,
                    "business_name": "E-commerce Store",
                    "integration_type": "FACEBOOK_PAGE",
                    "name": "Main Facebook Page",
                    "is_active": True,
                    "config": {
                        "auto_reply": True,
                        "webhook_enabled": True
                    },
                    "created_at": "2026-02-05T12:00:00Z",
                    "updated_at": "2026-02-05T12:00:00Z",
                    "last_synced_at": None,
                    "facebook_page_details": None
                },
                response_only=True
            )
        ],
        tags=['Integrations']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="List integrations",
        description="Get all active integrations for the specified business.",
        responses={200: IntegrationSerializer(many=True)},
        examples=[
            OpenApiExample(
                'List Integrations Response',
                value=[
                    {
                        "id": 1,
                        "business": 1,
                        "business_name": "E-commerce Store",
                        "integration_type": "FACEBOOK_PAGE",
                        "name": "Main Facebook Page",
                        "is_active": True,
                        "config": {},
                        "created_at": "2026-02-05T12:00:00Z",
                        "updated_at": "2026-02-05T12:00:00Z",
                        "last_synced_at": "2026-02-05T15:00:00Z",
                        "facebook_page_details": {
                            "page_id": "123456789",
                            "page_name": "My Business Page",
                            "page_category": "E-commerce",
                            "page_url": "https://facebook.com/mybusiness"
                        }
                    }
                ],
                response_only=True
            )
        ],
        tags=['Integrations']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        """Soft delete integration"""
        instance.is_active = False
        instance.save()

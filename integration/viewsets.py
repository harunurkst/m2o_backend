from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Platform, BusinessPlatform
from .serializers import PlatformSerializer, BusinessPlatformSerializer

class PlatformViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Platform CRUD operations.
    """
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all platforms",
        description="Retrieve a list of all available communication platforms.",
        tags=['Platforms']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a platform",
        description="Add a new communication platform to the system.",
        tags=['Platforms']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a platform",
        description="Get detailed information about a specific platform.",
        tags=['Platforms']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class BusinessPlatformViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BusinessPlatform management.
    Handles connections between businesses and platforms.
    """
    serializer_class = BusinessPlatformSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter business platforms based on the user's businesses.
        """
        user = self.request.user
        return BusinessPlatform.objects.filter(
            business__organization__members=user,
            is_active=True
        ).select_related('business', 'platform')

    @extend_schema(
        summary="List business platform connections",
        description="Retrieve all active platform connections for businesses associated with the user.",
        tags=['Business Platforms']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Connect business to platform",
        description="Create a new connection between a business and a communication platform.",
        tags=['Business Platforms']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

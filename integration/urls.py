from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PlatformViewSet, BusinessPlatformViewSet

router = DefaultRouter()
router.register(r'platforms', PlatformViewSet, basename='platform')

app_name = 'integration'

urlpatterns = [
    path('', include(router.urls)),
]

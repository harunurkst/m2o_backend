from rest_framework import permissions
from .models import OrganizationMembership


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """
    
    def has_object_permission(self, request, view, obj):
        # obj is an Organization instance
        return obj.members.filter(id=request.user.id).exists()


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission to check if user has admin or owner role in organization.
    """
    
    def has_object_permission(self, request, view, obj):
        # obj is an Organization instance
        membership = OrganizationMembership.objects.filter(
            user=request.user,
            organization=obj,
            role__in=[OrganizationMembership.Role.OWNER, OrganizationMembership.Role.ADMIN]
        ).exists()
        return membership


class IsBusinessOwner(permissions.BasePermission):
    """
    Permission to check if user owns the business through organization membership.
    """
    
    def has_object_permission(self, request, view, obj):
        # obj is a Business instance
        return obj.organization.members.filter(id=request.user.id).exists()


class CanManageIntegrations(permissions.BasePermission):
    """
    Permission to check if user can manage integrations.
    """
    
    def has_object_permission(self, request, view, obj):
        # obj is an Integration instance
        return obj.business.organization.members.filter(id=request.user.id).exists()

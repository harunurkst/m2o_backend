from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, EmailVerificationToken, Organization, OrganizationMembership,
    Business
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin for custom user model"""
    
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'is_verified']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    search_fields = ['email', 'first_name', 'last_name']
    filter_horizontal = ['groups', 'user_permissions']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for email verification tokens"""
    
    list_display = ['user', 'token', 'created_at', 'is_expired']
    list_filter = ['created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']


# ============================================================================
# Multi-Tenant Admin
# ============================================================================

class OrganizationMembershipInline(admin.TabularInline):
    """Inline admin for organization memberships"""
    model = OrganizationMembership
    extra = 1
    fields = ['user', 'role', 'joined_at', 'invited_by']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user', 'invited_by']


class BusinessInline(admin.TabularInline):
    """Inline admin for businesses within organization"""
    model = Business
    extra = 0
    fields = ['name', 'slug', 'is_active', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for organizations"""
    
    list_display = ['name', 'slug', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['owner']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'owner')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    inlines = [OrganizationMembershipInline, BusinessInline]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    """Admin for organization memberships"""
    
    list_display = ['user', 'organization', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'organization__name']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user', 'organization', 'invited_by']
    
    fieldsets = (
        (None, {'fields': ('user', 'organization', 'role')}),
        (_('Invitation Info'), {'fields': ('invited_by', 'joined_at')}),
    )



@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Admin for businesses"""
    
    list_display = ['name', 'organization', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'organization']
    search_fields = ['name', 'slug', 'organization__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['organization']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {'fields': ('organization', 'name', 'slug')}),
        (_('Details'), {'fields': ('description',)}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

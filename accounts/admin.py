from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, EmailVerificationToken


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
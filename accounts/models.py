from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model with email as username
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)
    
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class EmailVerificationToken(models.Model):
    """
    Store email verification tokens
    Simple approach instead of encoding in URL
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)


# ============================================================================
# Multi-Tenant Models
# ============================================================================

class Organization(models.Model):
    """
    Represents a tenant in the multi-tenant system.
    One user can own multiple organizations, and organizations can have multiple members.
    """
    name = models.CharField(_('organization name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, db_index=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,  # Prevent deletion of owner if they have organizations
        related_name='owned_organizations',
        verbose_name=_('owner')
    )
    members = models.ManyToManyField(
        CustomUser,
        through='OrganizationMembership',
        through_fields=('organization', 'user'),  # Specify which FK to use
        related_name='organizations',
        verbose_name=_('members')
    )
    
    # Soft delete
    is_active = models.BooleanField(_('active'), default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def clean(self):
        """Ensure owner is added as a member with OWNER role"""
        super().clean()
        # This validation happens in the signal after save


class OrganizationMembership(models.Model):
    """
    Through table for User-Organization many-to-many relationship.
    Adds role-based access control (RBAC) at organization level.
    """
    class Role(models.TextChoices):
        OWNER = 'OWNER', _('Owner')
        ADMIN = 'ADMIN', _('Admin')
        MEMBER = 'MEMBER', _('Member')
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        verbose_name=_('user')
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('organization')
    )
    role = models.CharField(
        _('role'),
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER
    )
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    invited_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_memberships',
        verbose_name=_('invited by')
    )
    
    class Meta:
        verbose_name = _('organization membership')
        verbose_name_plural = _('organization memberships')
        unique_together = [['user', 'organization']]
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['user', 'organization']),
            models.Index(fields=['organization', 'role']),
        ]
    
    def __str__(self):
        return f'{self.user.email} - {self.organization.name} ({self.role})'
    
    def clean(self):
        """Validate that organization owner has OWNER role"""
        super().clean()
        if self.organization.owner == self.user and self.role != self.Role.OWNER:
            raise ValidationError(_('Organization owner must have OWNER role'))


class Business(models.Model):
    """
    Represents a business entity within an organization.
    Multiple businesses can belong to one organization.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='businesses',
        verbose_name=_('organization')
    )
    name = models.CharField(_('business name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Soft delete
    is_active = models.BooleanField(_('active'), default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('business')
        verbose_name_plural = _('businesses')
        unique_together = [['organization', 'slug']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.organization.name} - {self.name}'
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

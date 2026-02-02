from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
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
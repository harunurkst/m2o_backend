import uuid
from django.utils import timezone
from datetime import timedelta
from django.db import models

from .managers import BusinessPlatformManager


class Platform(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    description_fr = models.CharField(max_length=500, blank=True, null=True) # French description
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    authorize_url = models.URLField(max_length=500, blank=True, null=True)
    redirect_url = models.URLField(max_length=500, blank=True, null=True)
    token_url = models.URLField(max_length=500, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_post = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert the name attribute to lowercase
        self.name = self.name.lower()
        super(Platform, self).save(*args, **kwargs)

    def get_description(self, lang_code):
        """
        Get the description in the given language code.
        """
        if lang_code == 'fr':
            return self.description_fr
        return self.description
    

PLATFORM_TYPE = (
     ('user', 'User'),
     ('page', 'Page'),
)

class BusinessPlatform(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    business = models.ForeignKey('accounts.Business', on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    access_token_secret = models.CharField(max_length=500, blank=True, null=True)  # For OAuth 1.0a (Twitter)
    expire_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    platform_type = models.CharField(max_length=100, choices=PLATFORM_TYPE)
    reconnection = models.BooleanField(default=False, db_index=True)
    
    # Generic fields for storing external platform entity information (like pages, channels, etc.)
    external_id = models.CharField(max_length=100, blank=True, null=True)  # Store external platform entity ID
    external_name = models.CharField(max_length=255, blank=True, null=True)  # Store external platform entity name
    # field to store the profile picture path
    external_profile_picture = models.ImageField(upload_to="user_platform/profile/", blank=True, null=True)

    objects =  BusinessPlatformManager()

    def __str__(self):
        return f"{self.business.name} - {self.platform.name}"

    def is_token_expired(self):
        if not self.expire_at:
            return False
        return timezone.now() >= self.expire_at
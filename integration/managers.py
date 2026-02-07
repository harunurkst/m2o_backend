from django.utils import timezone
from datetime import timedelta
from django.db import models


class BusinessPlatformManager(models.Manager):
    def create_business_platform(self, business, platform, response_data, platform_type):
        access_token = response_data['access_token']
        refresh_token = response_data.get('refresh_token')
        expires_in = response_data.get('expires_in')

        if expires_in:
            # Calculate the expiration time
            expire_at = timezone.now() + timedelta(seconds=expires_in)
        else:
            expire_at = None
        if business:
            # Use update_or_create logic in the manager
            obj, created = self.update_or_create(
                business=business,
                platform=platform,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expire_at': expire_at,
                    'platform_type': platform_type,
                }
            )
            
            # Track platform connection in user memory
            if created:
                try:
                    from memory.services.user_memory_service import UserMemoryService
                    memory_service = UserMemoryService()
                    memory_service.track_platform_connection(
                        user_uuid=user_uuid,
                        platform=platform.name if hasattr(platform, 'name') else str(platform)
                    )
                except Exception as e:
                    # Silently fail if memory service is not available
                    pass
        else:
            obj = self.create(
                platform=platform,
                access_token=access_token,
                refresh_token=refresh_token,
                expire_at=expire_at,
                platform_type=platform_type
            )
        return obj

    def update_business_platform(self, business_platform, response_data):
        """
        Update an existing user platform instance with new access token, refresh token, and expiration time.
        """
        access_token = response_data['access_token']
        refresh_token = response_data.get('refresh_token')
        expires_in = response_data.get('expires_in')

        if expires_in:
            # Calculate the expiration time
            expire_at = timezone.now() + timedelta(seconds=expires_in)
        else:
            expire_at = None

        # Update the instance fields
        business_platform.access_token = access_token
        business_platform.refresh_token = refresh_token
        business_platform.expire_at = expire_at

        # Save the instance to persist changes
        business_platform.save()

        return business_platform

    def deactivate_platform(self, business_platform: 'BusinessPlatform') -> None:
        """
        Deactivate the given user platform and its parent platform if it exists.
        """
        if not business_platform:
            return

        # Deactivate the current platform
        business_platform.reconnection = True
        business_platform.is_active = False
        business_platform.save()

        # Deactivate parent platform for facebook because facebook_page is a child of facebook
        parent_platform = business_platform.platform.parent
        if parent_platform:
            try:
                self.filter(
                    business=business_platform.business,
                    platform=parent_platform,
                    is_active=True
                ).update(
                    reconnection=True,
                    is_active=False
                )
            except Exception as e:
                raise Exception(f"Error deactivating parent platform: {e}")

    def get_business_platform_by_external_id(self, business, platform, external_id):
        """
        Retrieve an alternative BusinessPlatform entry for the given business and platform.
        Ensures that an external ID exists.
        """
        return self.filter(
            business=business,
            platform=platform,
            external_id=external_id,
            is_active=True
        ).first()

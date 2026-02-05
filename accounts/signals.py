from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Organization, OrganizationMembership


@receiver(post_save, sender=Organization)
def create_owner_membership(sender, instance, created, **kwargs):
    """
    Automatically add the organization owner as a member with OWNER role.
    This ensures the owner always has access to their organization.
    """
    if created:
        OrganizationMembership.objects.get_or_create(
            user=instance.owner,
            organization=instance,
            defaults={
                'role': OrganizationMembership.Role.OWNER,
                'invited_by': None  # Owner is not invited, they created the org
            }
        )

# Multi-Tenant Database Schema - Usage Guide

This guide demonstrates how to use the multi-tenant database models in your Django application.

## Overview

The schema implements a hierarchical multi-tenant structure:
- **User** → **Organization** → **Business** → **Integration**

## Creating Organizations

### Method 1: Using Django ORM

```python
from accounts.models import Organization, CustomUser

# Get or create a user
user = CustomUser.objects.get(email='user@example.com')

# Create an organization
org = Organization.objects.create(
    name='My Company',
    slug='my-company',  # Optional, auto-generated from name
    owner=user,
    is_active=True
)

# The owner is automatically added as a member with OWNER role via signal
```

### Method 2: Using Django Admin

1. Navigate to `/admin/accounts/organization/`
2. Click "Add Organization"
3. Fill in the details (name, slug, owner)
4. Save - the owner is automatically added as a member

## Managing Organization Members

```python
from accounts.models import OrganizationMembership

# Add a new member to organization
membership = OrganizationMembership.objects.create(
    user=another_user,
    organization=org,
    role=OrganizationMembership.Role.ADMIN,  # or MEMBER
    invited_by=user
)

# List all members of an organization
members = org.memberships.all()
for membership in members:
    print(f"{membership.user.email} - {membership.role}")

# Check if user is a member
is_member = org.members.filter(id=user.id).exists()

# Get user's role in organization
membership = OrganizationMembership.objects.get(user=user, organization=org)
print(membership.role)  # OWNER, ADMIN, or MEMBER
```

## Creating Businesses

```python
from accounts.models import Business

# Create a business within an organization
business = Business.objects.create(
    organization=org,
    name='E-commerce Store',
    slug='ecommerce-store',  # Optional, auto-generated
    description='Our main online store',
    is_active=True
)

# List all businesses in an organization
businesses = org.businesses.filter(is_active=True)
```

## Creating Integrations

### Facebook Page Integration

```python
from accounts.models import Integration, FacebookPageIntegration

# Step 1: Create base integration
integration = Integration.objects.create(
    business=business,
    integration_type=Integration.IntegrationType.FACEBOOK_PAGE,
    name='Main Facebook Page',
    is_active=True,
    config={
        'auto_reply': True,
        'webhook_enabled': True
    }
)

# Step 2: Create Facebook-specific details
fb_integration = FacebookPageIntegration.objects.create(
    integration=integration,
    page_id='123456789',
    page_name='My Business Page',
    access_token='EAAxxxxxxxxxxxx',
    page_access_token='EAAyyyyyyyyy',
    page_category='E-commerce',
    page_url='https://facebook.com/mybusiness'
)

# Access Facebook details from integration
integration.facebook_page_details.page_name  # 'My Business Page'
```

## Querying Data (Multi-Tenant Aware)

### Get User's Organizations

```python
# Get all organizations where user is a member
user_orgs = user.organizations.filter(is_active=True)

# Get organizations owned by user
owned_orgs = user.owned_organizations.filter(is_active=True)

# Get organizations where user is admin or owner
admin_orgs = user.organizations.filter(
    organizationmembership__role__in=[
        OrganizationMembership.Role.OWNER,
        OrganizationMembership.Role.ADMIN
    ]
)
```

### Get Organization's Businesses

```python
# Get all active businesses in organization
businesses = Business.objects.filter(
    organization=org,
    is_active=True
)

# With prefetch for performance
from django.db.models import Prefetch

orgs = Organization.objects.prefetch_related(
    Prefetch('businesses', queryset=Business.objects.filter(is_active=True))
).filter(owner=user)
```

### Get Business Integrations

```python
# Get all active integrations for a business
integrations = Integration.objects.filter(
    business=business,
    is_active=True
)

# Get only Facebook integrations
fb_integrations = Integration.objects.filter(
    business=business,
    integration_type=Integration.IntegrationType.FACEBOOK_PAGE,
    is_active=True
).select_related('facebook_page_details')

# Access Facebook details
for integration in fb_integrations:
    fb_details = integration.facebook_page_details
    print(f"Page: {fb_details.page_name} (ID: {fb_details.page_id})")
```

## Soft Delete Pattern

All models support soft delete via the `is_active` flag:

```python
# Soft delete (recommended)
organization.is_active = False
organization.save()

# Query only active records
active_orgs = Organization.objects.filter(is_active=True)

# Include inactive records
all_orgs = Organization.objects.all()

# Restore soft-deleted record
organization.is_active = True
organization.save()
```

## Multi-Tenant Isolation Example

Here's a complete example of tenant-isolated queries:

```python
def get_user_business_integrations(user, organization_slug, business_slug):
    """
    Get integrations for a specific business, ensuring user has access.
    This demonstrates proper multi-tenant isolation.
    """
    try:
        # Verify user is member of organization
        organization = Organization.objects.get(
            slug=organization_slug,
            members=user,
            is_active=True
        )
        
        # Get business within that organization
        business = Business.objects.get(
            slug=business_slug,
            organization=organization,
            is_active=True
        )
        
        # Get integrations for that business
        integrations = Integration.objects.filter(
            business=business,
            is_active=True
        ).select_related('business', 'business__organization')
        
        return integrations
        
    except (Organization.DoesNotExist, Business.DoesNotExist):
        return None
```

## Performance Optimization

### Use select_related and prefetch_related

```python
# Efficient query with joins
integrations = Integration.objects.select_related(
    'business',
    'business__organization',
    'business__organization__owner'
).filter(business__organization__members=user)

# Prefetch related data
organizations = Organization.objects.prefetch_related(
    'businesses',
    'businesses__integrations',
    'memberships__user'
).filter(owner=user)
```

### Database Indexes

The models include optimized indexes for common queries:
- `Organization`: indexed on `owner`, `slug`, `(owner, is_active)`
- `Business`: indexed on `(organization, is_active)`
- `Integration`: indexed on `business`, `integration_type`, `(business, integration_type)`

## Security Best Practices

### 1. Always Validate Organization Access

```python
def user_has_org_access(user, organization):
    """Check if user is a member of organization"""
    return organization.members.filter(id=user.id).exists()

def user_has_admin_access(user, organization):
    """Check if user has admin or owner role"""
    return OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
        role__in=[
            OrganizationMembership.Role.OWNER,
            OrganizationMembership.Role.ADMIN
        ]
    ).exists()
```

### 2. Encrypt Sensitive Data

For production, use field-level encryption for credentials:

```bash
pip install django-fernet-fields
```

```python
from fernet_fields import EncryptedTextField

class FacebookPageIntegration(models.Model):
    access_token = EncryptedTextField()
    page_access_token = EncryptedTextField()
```

### 3. Never Expose Credentials in API

```python
# In serializers, exclude sensitive fields
class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        exclude = ['config']  # Don't expose config with credentials
```

## Running Migrations

After implementing the models, create and run migrations:

```bash
# Create migrations
python manage.py makemigrations accounts

# Review the migration file
python manage.py sqlmigrate accounts 0002

# Apply migrations
python manage.py migrate

# Verify in database
python manage.py dbshell
```

## Testing the Schema

```python
# Create test data
from accounts.models import *

# 1. Create users
user1 = CustomUser.objects.create_user(email='owner@example.com', password='pass')
user2 = CustomUser.objects.create_user(email='admin@example.com', password='pass')

# 2. Create organization
org = Organization.objects.create(name='Test Org', owner=user1)

# 3. Add admin member
OrganizationMembership.objects.create(
    user=user2, 
    organization=org, 
    role=OrganizationMembership.Role.ADMIN,
    invited_by=user1
)

# 4. Create business
business = Business.objects.create(
    organization=org,
    name='Test Business'
)

# 5. Create integration
integration = Integration.objects.create(
    business=business,
    integration_type=Integration.IntegrationType.FACEBOOK_PAGE,
    name='FB Page'
)

fb_details = FacebookPageIntegration.objects.create(
    integration=integration,
    page_id='123456',
    access_token='token123'
)

# Verify hierarchy
print(f"Organization: {org.name}")
print(f"Members: {org.members.count()}")
print(f"Businesses: {org.businesses.count()}")
print(f"Integrations: {business.integrations.count()}")
```

# Quick Start Guide - Multi-Tenant Database Schema

## Step 1: Create Migrations

```bash
cd /home/harun/Desktop/message2order/backend
python manage.py makemigrations accounts
```

Expected output:
```
Migrations for 'accounts':
  accounts/migrations/0002_organization_organizationmembership_business_integration_facebookpageintegration.py
    - Create model Organization
    - Create model OrganizationMembership
    - Create model Business
    - Create model Integration
    - Create model FacebookPageIntegration
```

## Step 2: Review Migration (Optional)

```bash
# View the SQL that will be executed
python manage.py sqlmigrate accounts 0002
```

## Step 3: Apply Migrations

```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying accounts.0002_organization_organizationmembership_business_integration_facebookpageintegration... OK
```

## Step 4: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

## Step 5: Test in Admin

```bash
python manage.py runserver
```

Navigate to: `http://localhost:8000/admin/`

### Test Hierarchy:
1. **Create Organization** → Owner auto-added as member ✓
2. **Add Members** → Assign roles (ADMIN/MEMBER)
3. **Create Business** → Within the organization
4. **Create Integration** → Facebook Page type
5. **Add FB Details** → Page ID, tokens, etc.

## Quick Test Script

```python
# Run in Django shell: python manage.py shell

from accounts.models import *

# 1. Get your user
user = CustomUser.objects.get(email='your@email.com')

# 2. Create organization
org = Organization.objects.create(
    name='My Company',
    owner=user
)
print(f"✓ Created: {org}")
print(f"✓ Owner auto-added as member: {org.members.count()} member(s)")

# 3. Create business
business = Business.objects.create(
    organization=org,
    name='E-commerce Store'
)
print(f"✓ Created: {business}")

# 4. Create Facebook integration
integration = Integration.objects.create(
    business=business,
    integration_type=Integration.IntegrationType.FACEBOOK_PAGE,
    name='Main FB Page'
)

fb = FacebookPageIntegration.objects.create(
    integration=integration,
    page_id='123456789',
    page_name='My Business Page',
    access_token='your_token_here'
)
print(f"✓ Created: {fb}")

# Verify hierarchy
print(f"\n✓ Hierarchy verified:")
print(f"  - Organization: {org.name}")
print(f"  - Businesses: {org.businesses.count()}")
print(f"  - Integrations: {business.integrations.count()}")
```

## Common Issues

### Issue: "No such table: accounts_organization"
**Solution:** Run migrations first: `python manage.py migrate`

### Issue: "UNIQUE constraint failed"
**Solution:** Slug already exists. Use a different name or specify a unique slug.

### Issue: "Cannot delete user - PROTECT constraint"
**Solution:** User owns organizations. Delete organizations first or reassign ownership.

## Next Steps

- ✅ Migrations applied
- ✅ Test data created
- ⬜ Add API endpoints (optional)
- ⬜ Add field-level encryption for credentials (production)
- ⬜ Add middleware for organization context (optional)

## Documentation

- **Full Usage Guide**: [`MULTI_TENANT_USAGE.md`](file:///home/harun/Desktop/message2order/backend/MULTI_TENANT_USAGE.md)
- **Implementation Details**: See artifacts in conversation

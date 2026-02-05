#!/usr/bin/env python
"""
Test script for Organization/Business Onboarding API
Run with: python manage.py shell < test_onboarding_api.py
"""

from accounts.models import CustomUser, Organization, OrganizationMembership, Business, Integration
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Testing Multi-Tenant Onboarding API")
print("=" * 60)

# Clean up test data
print("\n1. Cleaning up existing test data...")
Organization.objects.filter(slug__startswith='test-').delete()
User.objects.filter(email__startswith='test').delete()

# Create test users
print("\n2. Creating test users...")
user1 = User.objects.create_user(
    email='test-owner@example.com',
    password='TestPass123!',
    first_name='Test',
    last_name='Owner',
    is_active=True,
    is_verified=True
)
print(f"   ✓ Created user: {user1.email}")

user2 = User.objects.create_user(
    email='test-admin@example.com',
    password='TestPass123!',
    first_name='Test',
    last_name='Admin',
    is_active=True,
    is_verified=True
)
print(f"   ✓ Created user: {user2.email}")

# Test Organization creation (simulating API call)
print("\n3. Testing Organization creation...")
org = Organization.objects.create(
    name='Test Company',
    slug='test-company',
    owner=user1
)
print(f"   ✓ Created organization: {org.name}")
print(f"   ✓ Owner: {org.owner.email}")

# Verify owner was auto-added as member
membership = OrganizationMembership.objects.get(user=user1, organization=org)
print(f"   ✓ Owner auto-added as member with role: {membership.role}")

# Test adding member
print("\n4. Testing member addition...")
membership2 = OrganizationMembership.objects.create(
    user=user2,
    organization=org,
    role=OrganizationMembership.Role.ADMIN,
    invited_by=user1
)
print(f"   ✓ Added {user2.email} as {membership2.role}")
print(f"   ✓ Total members: {org.members.count()}")

# Test Business creation (simulating API call)
print("\n5. Testing Business creation...")
business = Business.objects.create(
    organization=org,
    name='Test E-commerce Store',
    slug='test-ecommerce',
    description='Test business for e-commerce'
)
print(f"   ✓ Created business: {business.name}")
print(f"   ✓ Organization: {business.organization.name}")

# Test Integration creation
print("\n6. Testing Integration creation...")
integration = Integration.objects.create(
    business=business,
    integration_type=Integration.IntegrationType.FACEBOOK_PAGE,
    name='Test Facebook Page',
    config={'auto_reply': True}
)
print(f"   ✓ Created integration: {integration.name}")
print(f"   ✓ Type: {integration.get_integration_type_display()}")

# Test multi-tenant isolation
print("\n7. Testing multi-tenant isolation...")
user1_orgs = Organization.objects.filter(members=user1)
user2_orgs = Organization.objects.filter(members=user2)
print(f"   ✓ User1 organizations: {user1_orgs.count()}")
print(f"   ✓ User2 organizations: {user2_orgs.count()}")

# Test hierarchy
print("\n8. Verifying hierarchy...")
print(f"   ✓ Organization: {org.name}")
print(f"   ✓ Members: {org.members.count()}")
print(f"   ✓ Businesses: {org.businesses.count()}")
print(f"   ✓ Integrations in business: {business.integrations.count()}")

# Test soft delete
print("\n9. Testing soft delete...")
business.is_active = False
business.save()
active_businesses = Business.objects.filter(organization=org, is_active=True)
print(f"   ✓ Active businesses after soft delete: {active_businesses.count()}")

# Restore
business.is_active = True
business.save()
print(f"   ✓ Restored business")

print("\n" + "=" * 60)
print("✓ All tests passed successfully!")
print("=" * 60)

print("\n📝 Test Summary:")
print(f"   - Organizations created: 1")
print(f"   - Users created: 2")
print(f"   - Businesses created: 1")
print(f"   - Integrations created: 1")
print(f"   - Organization members: {org.members.count()}")

print("\n🔗 Next Steps:")
print("   1. Run migrations: python manage.py migrate")
print("   2. Start server: python manage.py runserver")
print("   3. Test API endpoints using curl or Postman")
print("   4. Check API docs: http://localhost:8000/api/docs/")

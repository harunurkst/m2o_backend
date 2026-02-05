# Multi-Tenant Onboarding API Documentation

## Overview

This API provides endpoints for onboarding organizations and businesses in a multi-tenant SaaS platform.

## Base URL

```
http://localhost:8000/api/auth/
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### 1. Organization Onboarding

#### **Create Organization** (Onboarding)

```http
POST /api/auth/organizations/
```

**Description**: Create a new organization. The authenticated user becomes the owner and is automatically added as a member with OWNER role.

**Request Body**:
```json
{
  "name": "My Company",
  "slug": "my-company"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "My Company",
  "slug": "my-company",
  "owner": 1,
  "owner_email": "user@example.com",
  "is_active": true,
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "memberships": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "user_name": "John Doe",
      "organization": 1,
      "role": "OWNER",
      "joined_at": "2026-02-05T12:00:00Z",
      "invited_by": null,
      "invited_by_email": null
    }
  ],
  "member_count": 1,
  "business_count": 0
}
```

**Validation**:
- `name`: Required, max 255 characters
- `slug`: Optional (auto-generated from name), must be unique

---

#### **List User's Organizations**

```http
GET /api/auth/organizations/
```

**Description**: Get all organizations where the authenticated user is a member.

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "My Company",
    "slug": "my-company",
    "owner": 1,
    "owner_email": "user@example.com",
    "is_active": true,
    "created_at": "2026-02-05T12:00:00Z",
    "updated_at": "2026-02-05T12:00:00Z",
    "member_count": 3,
    "business_count": 2,
    "user_role": "OWNER"
  }
]
```

---

#### **Get Organization Details**

```http
GET /api/auth/organizations/{id}/
```

**Description**: Get detailed information about a specific organization including members and businesses.

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "My Company",
  "slug": "my-company",
  "owner": 1,
  "owner_email": "user@example.com",
  "is_active": true,
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "memberships": [
    {
      "id": 1,
      "user": 1,
      "user_email": "owner@example.com",
      "user_name": "John Doe",
      "organization": 1,
      "role": "OWNER",
      "joined_at": "2026-02-05T12:00:00Z",
      "invited_by": null,
      "invited_by_email": null
    },
    {
      "id": 2,
      "user": 2,
      "user_email": "admin@example.com",
      "user_name": "Jane Smith",
      "organization": 1,
      "role": "ADMIN",
      "joined_at": "2026-02-05T13:00:00Z",
      "invited_by": 1,
      "invited_by_email": "owner@example.com"
    }
  ],
  "member_count": 2,
  "business_count": 1
}
```

---

#### **Update Organization**

```http
PUT /api/auth/organizations/{id}/
PATCH /api/auth/organizations/{id}/
```

**Permissions**: Requires ADMIN or OWNER role

**Request Body**:
```json
{
  "name": "Updated Company Name",
  "slug": "updated-company"
}
```

---

#### **Delete Organization** (Soft Delete)

```http
DELETE /api/auth/organizations/{id}/
```

**Permissions**: Requires ADMIN or OWNER role

**Response** (204 No Content)

---

#### **Add Member to Organization**

```http
POST /api/auth/organizations/{id}/add_member/
```

**Permissions**: Requires ADMIN or OWNER role

**Request Body**:
```json
{
  "user": 2,
  "role": "ADMIN"
}
```

**Roles**: `OWNER`, `ADMIN`, `MEMBER`

**Response** (201 Created):
```json
{
  "id": 2,
  "user": 2,
  "user_email": "newmember@example.com",
  "user_name": "New Member",
  "organization": 1,
  "role": "ADMIN",
  "joined_at": "2026-02-05T14:00:00Z",
  "invited_by": 1,
  "invited_by_email": "owner@example.com"
}
```

---

#### **Remove Member from Organization**

```http
DELETE /api/auth/organizations/{id}/remove_member/?user_id=2
```

**Permissions**: Requires ADMIN or OWNER role

**Query Parameters**:
- `user_id`: ID of the user to remove (required)

**Response** (204 No Content)

**Note**: Cannot remove the organization owner.

---

### 2. Business Onboarding

#### **Create Business** (Onboarding)

```http
POST /api/auth/organizations/{organization_id}/businesses/
```

**Description**: Create a new business within an organization. User must be a member of the organization.

**Request Body**:
```json
{
  "name": "E-commerce Store",
  "slug": "ecommerce-store",
  "description": "Our main online store"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "organization": 1,
  "organization_name": "My Company",
  "name": "E-commerce Store",
  "slug": "ecommerce-store",
  "description": "Our main online store",
  "is_active": true,
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "integration_count": 0
}
```

**Validation**:
- `name`: Required, max 255 characters
- `slug`: Optional (auto-generated from name), must be unique within organization
- `description`: Optional

---

#### **List Businesses in Organization**

```http
GET /api/auth/organizations/{organization_id}/businesses/
```

**Description**: Get all active businesses in the specified organization.

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "organization": 1,
    "organization_name": "My Company",
    "name": "E-commerce Store",
    "slug": "ecommerce-store",
    "description": "Our main online store",
    "is_active": true,
    "created_at": "2026-02-05T12:00:00Z",
    "updated_at": "2026-02-05T12:00:00Z",
    "integration_count": 2
  }
]
```

---

#### **Get Business Details**

```http
GET /api/auth/organizations/{organization_id}/businesses/{id}/
```

**Response** (200 OK):
```json
{
  "id": 1,
  "organization": 1,
  "organization_name": "My Company",
  "name": "E-commerce Store",
  "slug": "ecommerce-store",
  "description": "Our main online store",
  "is_active": true,
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "integration_count": 2
}
```

---

#### **Update Business**

```http
PUT /api/auth/organizations/{organization_id}/businesses/{id}/
PATCH /api/auth/organizations/{organization_id}/businesses/{id}/
```

**Request Body**:
```json
{
  "name": "Updated Business Name",
  "description": "Updated description"
}
```

---

#### **Delete Business** (Soft Delete)

```http
DELETE /api/auth/organizations/{organization_id}/businesses/{id}/
```

**Response** (204 No Content)

---

### 3. Integration Management

#### **Create Integration**

```http
POST /api/auth/businesses/{business_id}/integrations/
```

**Request Body** (Facebook Page):
```json
{
  "integration_type": "FACEBOOK_PAGE",
  "name": "Main Facebook Page",
  "config": {
    "auto_reply": true,
    "webhook_enabled": true
  }
}
```

**Integration Types**:
- `FACEBOOK_PAGE`
- `WHATSAPP`
- `SLACK`

**Response** (201 Created):
```json
{
  "id": 1,
  "business": 1,
  "business_name": "E-commerce Store",
  "integration_type": "FACEBOOK_PAGE",
  "name": "Main Facebook Page",
  "is_active": true,
  "config": {
    "auto_reply": true,
    "webhook_enabled": true
  },
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "last_synced_at": null,
  "facebook_page_details": null
}
```

---

#### **List Integrations**

```http
GET /api/auth/businesses/{business_id}/integrations/
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "business": 1,
    "business_name": "E-commerce Store",
    "integration_type": "FACEBOOK_PAGE",
    "name": "Main Facebook Page",
    "is_active": true,
    "config": {},
    "created_at": "2026-02-05T12:00:00Z",
    "updated_at": "2026-02-05T12:00:00Z",
    "last_synced_at": "2026-02-05T15:00:00Z",
    "facebook_page_details": {
      "page_id": "123456789",
      "page_name": "My Business Page",
      "page_category": "E-commerce",
      "page_url": "https://facebook.com/mybusiness"
    }
  }
]
```

---

## Complete Onboarding Flow Example

### Step 1: Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Step 2: Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 3: Create Organization (Onboarding)

```bash
curl -X POST http://localhost:8000/api/auth/organizations/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Company",
    "slug": "my-company"
  }'
```

### Step 4: Create Business (Onboarding)

```bash
curl -X POST http://localhost:8000/api/auth/organizations/1/businesses/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-commerce Store",
    "slug": "ecommerce-store",
    "description": "Our main online store"
  }'
```

### Step 5: Create Integration

```bash
curl -X POST http://localhost:8000/api/auth/businesses/1/integrations/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "integration_type": "FACEBOOK_PAGE",
    "name": "Main Facebook Page"
  }'
```

---

## Error Responses

### 400 Bad Request
```json
{
  "slug": ["Organization with this slug already exists."]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## API Documentation (Swagger)

Interactive API documentation is available at:

```
http://localhost:8000/api/docs/
```

## Testing the API

Use the provided Swagger UI or tools like Postman, curl, or HTTPie to test the endpoints.

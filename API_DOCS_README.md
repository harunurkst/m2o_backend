# API Documentation with drf-spectacular

## Overview

The API is fully documented using **drf-spectacular** with comprehensive request/response examples.

## Accessing API Documentation

### Swagger UI (Interactive)
```
http://localhost:8000/api/docs/
```
- Interactive API testing interface
- Try out endpoints directly from the browser
- View request/response schemas with examples
- JWT authentication support built-in

### ReDoc (Documentation)
```
http://localhost:8000/api/redoc/
```
- Clean, readable API documentation
- Better for reading and understanding the API
- Organized by tags (Organizations, Businesses, Integrations)

### OpenAPI Schema (JSON)
```
http://localhost:8000/api/schema/
```
- Raw OpenAPI 3.0 schema
- Can be imported into Postman, Insomnia, etc.

## API Tags

The API is organized into the following sections:

### 1. **Authentication**
- User registration, login, email verification
- JWT token management

### 2. **Organizations**
- Create organization (onboarding)
- List user's organizations
- Get organization details
- Add/remove members
- Update/delete organizations

### 3. **Businesses**
- Create business (onboarding)
- List businesses in organization
- Get business details
- Update/delete businesses

### 4. **Integrations**
- Create integrations (Facebook, WhatsApp, Slack)
- List integrations for business
- Get integration details
- Update/delete integrations

## Request/Response Examples

All endpoints include comprehensive examples:

### Create Organization Example

**Request:**
```json
{
  "name": "My Company",
  "slug": "my-company"
}
```

**Response (201):**
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

### Create Business Example

**Request:**
```json
{
  "name": "E-commerce Store",
  "slug": "ecommerce-store",
  "description": "Our main online store"
}
```

**Response (201):**
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

## Using Swagger UI

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to Swagger UI:**
   ```
   http://localhost:8000/api/docs/
   ```

3. **Authenticate:**
   - Click the "Authorize" button (top right)
   - Login first via `/api/auth/login/` to get JWT token
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

4. **Test Endpoints:**
   - Expand any endpoint
   - Click "Try it out"
   - Fill in the request body (examples provided)
   - Click "Execute"
   - View the response

## Features

✅ **Comprehensive Examples** - Every endpoint has request/response examples  
✅ **Interactive Testing** - Test endpoints directly from Swagger UI  
✅ **JWT Authentication** - Built-in authentication support  
✅ **Organized by Tags** - Easy navigation by feature area  
✅ **Auto-generated** - Documentation stays in sync with code  
✅ **Multiple Formats** - Swagger UI, ReDoc, and raw OpenAPI schema  

## Schema Decorators Used

All ViewSets use `@extend_schema` decorators with:
- `summary` - Short endpoint description
- `description` - Detailed explanation
- `request` - Request serializer
- `responses` - Response serializers with status codes
- `examples` - OpenApiExample for request/response
- `tags` - Organization into sections
- `parameters` - Query/path parameters

## No Markdown Files

All documentation is generated automatically from the code using drf-spectacular decorators. No separate markdown documentation files are needed - everything is in Swagger UI!

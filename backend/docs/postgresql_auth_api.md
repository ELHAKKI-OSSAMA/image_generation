# PostgreSQL Authentication API Documentation

## Overview
This documentation details the PostgreSQL-based authentication system that supports three distinct user roles:
1. Admin - System administrators
2. Organization - Organization administrators
3. User - Regular organization members

## Base URL
```
http://localhost:8000/postgresql-auth
```

## Security Implementation

### Password Security
- Passwords are hashed using bcrypt algorithm
- Salt rounds are automatically managed by the bcrypt implementation
- Original passwords are never stored in the database

### JWT (JSON Web Token)
- Token algorithm: HS256
- Token expiration: 30 minutes
- Token structure:
  ```json
  {
    "sub": "user@example.com",  // subject (user email)
    "role": "admin",  // user role (admin, organization, or user)
    "exp": 1679236432  // expiration timestamp
  }
  ```

### Role-Based Access
- Three distinct roles: admin, organization, user
- Each role has its own registration endpoint
- Role information is encoded in JWT tokens
- Role-specific database tables

## API Endpoints

### 1. Register Admin
**Endpoint:** `POST /postgresql-auth/register/admin`

**Description:** Creates a new admin account.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "email": "admin@example.com",
    "password": "secure_password",
    "first_name": "Admin",
    "last_name": "User"
}
```

**Success Response (200 OK):**
```json
{
    "id": "987fcdeb-51a2-4bcd-9876-543210fedcba",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "organization_id": null
}
```

### 2. Register Organization
**Endpoint:** `POST /postgresql-auth/register/organization`

**Description:** Creates a new organization and its admin account.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "email": "org@example.com",
    "password": "secure_password",
    "first_name": "Org",
    "last_name": "Admin",
    "organization_name": "Example Organization",
    "phone": "+1234567890"
}
```

**Success Response (200 OK):**
```json
{
    "id": "987fcdeb-51a2-4bcd-9876-543210fedcba",
    "email": "org@example.com",
    "first_name": "Org",
    "last_name": "Admin",
    "role": "organization",
    "organization_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 3. Register User
**Endpoint:** `POST /postgresql-auth/register/user`

**Description:** Creates a new user account within an organization.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "Regular",
    "last_name": "User",
    "organization_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Success Response (200 OK):**
```json
{
    "id": "987fcdeb-51a2-4bcd-9876-543210fedcba",
    "email": "user@example.com",
    "first_name": "Regular",
    "last_name": "User",
    "role": "user",
    "organization_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 4. User Login
**Endpoint:** `POST /postgresql-auth/login`

**Description:** Authenticates user (any role) and provides JWT access token.

**Request Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (form-data):**
- `username`: User's email address
- `password`: User's password

**Success Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 5. Get Current User Profile
**Endpoint:** `GET /postgresql-auth/me`

**Description:** Retrieves the profile of the currently authenticated user.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
    "id": "987fcdeb-51a2-4bcd-9876-543210fedcba",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Name",
    "role": "user",  // or "admin" or "organization"
    "organization_id": "123e4567-e89b-12d3-a456-426614174000"  // null for admins
}
```

## Organization Verification API

### 1. Submit Organization Verification
**Endpoint:** `POST /api/v1/organizations/submit-verification`

**Description:** Submit organization verification documents and details.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "business_type": "corporation",
    "business_description": "AI Image Generation Company",
    "documents": [
        {
            "document_type": "business_license",
            "file_url": "https://example.com/license.pdf",
            "file_name": "business_license.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024
        }
    ]
}
```

**Success Response (200 OK):**
```json
{
    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_review",
    "verification_submitted_at": "2025-03-14T16:00:00Z",
    "verification_notes": null,
    "business_type": "corporation",
    "business_description": "AI Image Generation Company",
    "approved_by": null,
    "approved_at": null,
    "rejected_reason": null,
    "rejected_at": null,
    "documents": [
        {
            "id": "987fcdeb-51a2-4bcd-9876-543210fedcba",
            "document_type": "business_license",
            "file_url": "https://example.com/license.pdf",
            "file_name": "business_license.pdf",
            "verification_status": "in_review"
        }
    ]
}
```

### 2. Get Verification Status
**Endpoint:** `GET /api/v1/organizations/verification-status`

**Description:** Check the current verification status of an organization.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_review",
    "verification_submitted_at": "2025-03-14T16:00:00Z",
    "verification_notes": null,
    "business_type": "corporation",
    "business_description": "AI Image Generation Company",
    "approved_by": null,
    "approved_at": null,
    "rejected_reason": null,
    "rejected_at": null,
    "documents": [...]
}
```

### 3. Admin: Approve Verification
**Endpoint:** `POST /api/v1/admin/verifications/{org_id}/approve`

**Description:** Approve an organization's verification request (Admin only).

**Request Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "notes": "All documents verified successfully"
}
```

**Success Response (200 OK):**
```json
{
    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "approved",
    "verification_notes": "All documents verified successfully",
    "approved_by": "987fcdeb-51a2-4bcd-9876-543210fedcba",
    "approved_at": "2025-03-14T16:10:00Z"
}
```

### 4. Admin: Reject Verification
**Endpoint:** `POST /api/v1/admin/verifications/{org_id}/reject`

**Description:** Reject an organization's verification request (Admin only).

**Request Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "notes": "Business license expired"
}
```

**Success Response (200 OK):**
```json
{
    "organization_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "rejected",
    "verification_notes": "Business license expired",
    "rejected_at": "2025-03-14T16:10:00Z"
}
```

## Subscription Management API

### 1. Create Subscription Plan (Admin)
**Endpoint:** `POST /api/v1/admin/subscription-plans`

**Description:** Create a new subscription plan (Admin only).

**Request Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "Premium",
    "tier": "premium",
    "price_monthly": 99,
    "price_yearly": 990,
    "max_users": 10,
    "max_storage_gb": 100,
    "max_api_calls_per_month": 10000,
    "features": {
        "priority_support": true,
        "custom_models": true
    }
}
```

### 2. List Subscription Plans
**Endpoint:** `GET /api/v1/organizations/subscription-plans`

**Description:** Get list of available subscription plans.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

### 3. Get Current Subscription
**Endpoint:** `GET /api/v1/organizations/current-subscription`

**Description:** Get organization's current subscription details and usage.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

### 4. Update Subscription
**Endpoint:** `POST /api/v1/organizations/update-subscription`

**Description:** Update organization's subscription plan.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "plan_id": "123e4567-e89b-12d3-a456-426614174000",
    "billing_cycle": "monthly",
    "billing_info": {
        "billing_email": "billing@example.com",
        "billing_address": "123 Main St, City, Country",
        "payment_method_id": "pm_123456789"
    }
}
```

### 5. Cancel Subscription
**Endpoint:** `POST /api/v1/organizations/cancel-subscription`

**Description:** Cancel organization's current subscription.

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "cancellation_reason": "Switching to different service",
    "feedback": "Great service but need different features"
}
```

### 6. Get Subscription History
**Endpoint:** `GET /api/v1/organizations/subscription-history`

**Description:** Get organization's subscription history.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

## Testing Guide

### Using Postman Collection
1. Import the provided `PostgreSQL_Auth_API.postman_collection.json` file into Postman
2. Create an environment with variable `base_url` set to `http://localhost:8000`
3. The collection includes pre-configured requests for all endpoints
4. Tests automatically save tokens to environment variables

### Testing Flow

1. **Admin Flow**
   ```bash
   # 1. Register Admin
   curl -X POST http://localhost:8000/postgresql-auth/register/admin \
   -H "Content-Type: application/json" \
   -d '{
       "email": "admin@example.com",
       "password": "admin_password",
       "first_name": "Admin",
       "last_name": "User"
   }'

   # Expected Success Response: 200 OK
   {
       "id": "uuid-here",
       "email": "admin@example.com",
       "role": "admin"
   }

   # Expected Error (Email exists): 400 Bad Request
   {
       "detail": "Email already registered"
   }

   # 2. Admin Login
   curl -X POST http://localhost:8000/postgresql-auth/login \
   -d "username=admin@example.com" \
   -d "password=admin_password"

   # Save the token for next requests
   export TOKEN="returned_token_here"

   # 3. Get Admin Profile
   curl http://localhost:8000/postgresql-auth/me \
   -H "Authorization: Bearer $TOKEN"
   ```

2. **Organization Flow**
   ```bash
   # 1. Register Organization
   curl -X POST http://localhost:8000/postgresql-auth/register/organization \
   -H "Content-Type: application/json" \
   -d '{
       "email": "org@example.com",
       "password": "org_password",
       "first_name": "Org",
       "last_name": "Admin",
       "organization_name": "Test Org",
       "phone": "+1234567890"
   }'

   # Save organization ID for user registration
   export ORG_ID="returned_org_id_here"

   # 2. Organization Login
   curl -X POST http://localhost:8000/postgresql-auth/login \
   -d "username=org@example.com" \
   -d "password=org_password"

   # Save new token
   export TOKEN="returned_token_here"
   ```

3. **User Flow**
   ```bash
   # 1. Register User (needs organization ID)
   curl -X POST http://localhost:8000/postgresql-auth/register/user \
   -H "Content-Type: application/json" \
   -d '{
       "email": "user@example.com",
       "password": "user_password",
       "first_name": "Regular",
       "last_name": "User",
       "organization_id": "'$ORG_ID'"
   }'

   # Expected Error (Invalid Org ID): 400 Bad Request
   {
       "detail": "Invalid organization ID"
   }

   # 2. User Login
   curl -X POST http://localhost:8000/postgresql-auth/login \
   -d "username=user@example.com" \
   -d "password=user_password"
   ```

### Common Error Cases

1. **Authentication Errors**
   ```json
   // Invalid credentials
   {
       "detail": "Incorrect email or password"
   }

   // Missing token
   {
       "detail": "Not authenticated"
   }

   // Invalid token
   {
       "detail": "Could not validate credentials"
   }
   ```

2. **Authorization Errors**
   ```json
   // Insufficient permissions
   {
       "detail": "Not enough permissions"
   }

   // Invalid role
   {
       "detail": "Invalid role specified"
   }
   ```

3. **Validation Errors**
   ```json
   // Invalid email format
   {
       "detail": "Invalid email format"
   }

   // Password too short
   {
       "detail": "Password must be at least 8 characters"
   }

   // Missing required fields
   {
       "detail": "Field required"
   }
   ```

### Testing Tips
1. Test registration with invalid data formats
2. Test login with incorrect credentials
3. Test protected endpoints without token
4. Test role-specific endpoints with wrong role tokens
5. Test organization user registration with invalid org ID
6. Test duplicate email registrations

### Using Environment Variables
Create a `.env` file for testing:
```bash
# Test Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin_password

# Test Organization
ORG_EMAIL=org@example.com
ORG_PASSWORD=org_password
ORG_NAME="Test Organization"

# Test User
USER_EMAIL=user@example.com
USER_PASSWORD=user_password
```

## Testing in Postman

### Step 1: Create an Admin
1. Create a new POST request
2. URL: `http://localhost:8000/postgresql-auth/register/admin`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
       "email": "admin@example.com",
       "password": "admin_password",
       "first_name": "Admin",
       "last_name": "User"
   }
   ```

### Step 2: Create an Organization
1. Create a new POST request
2. URL: `http://localhost:8000/postgresql-auth/register/organization`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
       "email": "org@example.com",
       "password": "org_password",
       "first_name": "Org",
       "last_name": "Admin",
       "organization_name": "Test Organization",
       "phone": "+1234567890"
   }
   ```
5. Save the returned `organization_id`

### Step 3: Create a Regular User
1. Create a new POST request
2. URL: `http://localhost:8000/postgresql-auth/register/user`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
       "email": "user@example.com",
       "password": "user_password",
       "first_name": "Regular",
       "last_name": "User",
       "organization_id": "paste-organization-id-here"
   }
   ```

### Step 4: Login (Any Role)
1. Create a new POST request
2. URL: `http://localhost:8000/postgresql-auth/login`
3. Body type: `x-www-form-urlencoded`
4. Add form fields:
   - Key: `username`, Value: your email
   - Key: `password`, Value: your password
5. Send request and save the returned access token

### Step 5: Get User Profile
1. Create a new GET request
2. URL: `http://localhost:8000/postgresql-auth/me`
3. Headers:
   ```
   Authorization: Bearer your-access-token-here
   ```

## Common Issues and Solutions

### 1. Role-specific Registration Errors
- "Email already registered" - Email is already used in any role
- "Invalid organization ID" - When registering a user with non-existent organization
- "Organization name required" - When registering an organization

### 2. Login Issues
- System tries admin login first, then organization/user login
- Make sure to use the correct email/password combination
- Token includes role information for proper authorization

### 3. Profile Access Issues
- Token must include valid role information
- Organization ID will be null for admin users
- Regular users must belong to an organization

## Database Schema

### Admin Table
```sql
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);
```

### Organization Table
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    approved_by UUID REFERENCES admins(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    subscription_tier VARCHAR(50) DEFAULT 'trial',
    max_users INTEGER DEFAULT 5,
    max_storage_gb INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Organization Member Table
```sql
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    firebase_uid VARCHAR(255) UNIQUE
);

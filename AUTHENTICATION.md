# AWS Cognito Authentication Setup

## Overview

Complete user authentication system using AWS Cognito with:
- User signup/login
- Email verification
- Password reset
- JWT token authentication
- User roles (admin, users, premium)
- Protected API endpoints

## Features

### User Management
- Email-based signup
- Password requirements (8+ chars, uppercase, lowercase, numbers, symbols)
- Email verification
- Password reset
- User groups (admin, users, premium)

### Authentication
- JWT tokens (access, ID, refresh)
- Token expiry (60 minutes)
- Refresh token (30 days)
- Secure token validation

### Authorization
- Role-based access control
- Admin-only endpoints
- Premium user features
- Public endpoints

## API Endpoints

### Public Endpoints

#### POST /auth/signup
Register new user
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

#### POST /auth/login
Login and get tokens
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:
```json
{
  "access_token": "eyJraWQ...",
  "id_token": "eyJraWQ...",
  "refresh_token": "eyJjdHk...",
  "token_type": "Bearer"
}
```

#### POST /auth/verify-email
Verify email with code
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

#### POST /auth/forgot-password
Request password reset
```json
{
  "email": "user@example.com"
}
```

#### POST /auth/reset-password
Reset password with code
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "NewSecurePass123!"
}
```

### Protected Endpoints (Require Authentication)

#### GET /auth/me
Get current user profile
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://gpt.vmind.online/auth/me
```

#### POST /generate
Generate text (authenticated users only)
```bash
curl -X POST https://gpt.vmind.online/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?", "max_tokens": 100}'
```

### Admin Endpoints (Require Admin Role)

#### GET /auth/users
List all users
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  https://gpt.vmind.online/auth/users
```

#### POST /auth/users/{email}/add-to-group
Add user to group
```bash
curl -X POST https://gpt.vmind.online/auth/users/user@example.com/add-to-group \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"group": "premium"}'
```

#### DELETE /auth/users/{email}
Delete user
```bash
curl -X DELETE https://gpt.vmind.online/auth/users/user@example.com \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## User Groups

### admin
- Full access to all endpoints
- User management
- System configuration

### users
- Default group for all users
- Access to generate endpoint
- Basic features

### premium
- Extended rate limits
- Priority processing
- Advanced features

## Setup

### 1. Deploy Infrastructure

Terraform automatically creates:
- Cognito User Pool
- App Client
- User Groups
- Hosted UI domain

### 2. Get Cognito Details

After deployment:
```bash
terraform output cognito_user_pool_id
terraform output cognito_client_id
terraform output cognito_domain
```

### 3. Configure Kubernetes Secrets

```bash
kubectl create secret generic cognito-secrets \
  --from-literal=user-pool-id=YOUR_USER_POOL_ID \
  --from-literal=client-id=YOUR_CLIENT_ID
```

### 4. Test Authentication

```bash
# Signup
curl -X POST https://gpt.vmind.online/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'

# Verify email (check your email for code)
curl -X POST https://gpt.vmind.online/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# Login
curl -X POST https://gpt.vmind.online/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Use access token for API calls
curl -X POST https://gpt.vmind.online/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "max_tokens": 50}'
```

## Frontend Integration

### JavaScript Example

```javascript
// Signup
async function signup(email, password, name) {
  const response = await fetch('https://gpt.vmind.online/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });
  return response.json();
}

// Login
async function login(email, password) {
  const response = await fetch('https://gpt.vmind.online/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
}

// Generate text
async function generate(prompt) {
  const token = localStorage.getItem('access_token');
  const response = await fetch('https://gpt.vmind.online/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ prompt, max_tokens: 100 })
  });
  return response.json();
}
```

## Security Features

1. **Password Policy**
   - Minimum 8 characters
   - Uppercase, lowercase, numbers, symbols required

2. **Email Verification**
   - Required before login
   - Prevents fake accounts

3. **Token Security**
   - JWT tokens with RS256
   - Short expiry (60 minutes)
   - Refresh tokens for renewal

4. **Advanced Security**
   - Brute force protection
   - Account takeover prevention
   - Compromised credentials check

5. **MFA Support**
   - Optional multi-factor authentication
   - TOTP-based

## Cost

- Cognito Free Tier: 50,000 MAUs (Monthly Active Users)
- After free tier: $0.0055 per MAU
- Example: 10,000 users = $55/month

## Monitoring

### CloudWatch Logs
- User signups
- Login attempts
- Failed authentications
- Token usage

### Metrics
- Active users
- Authentication success rate
- Token refresh rate

## Troubleshooting

### User can't login
- Check email verification status
- Verify password meets requirements
- Check user status in Cognito console

### Token expired
- Use refresh token to get new access token
- POST /auth/refresh with refresh_token

### Permission denied
- Check user groups
- Verify token is valid
- Check endpoint requires correct role

## Documentation

- API Docs: https://gpt.vmind.online/docs
- Cognito Console: AWS Console → Cognito
- User Pool ID: Check Terraform outputs

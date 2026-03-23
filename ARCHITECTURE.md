# System Architecture

ESE Booking System architecture overview and design decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • User Registration & Login                              │   │
│  │  • Profile Management                                     │   │
│  │  • Password Reset Flow                                    │   │
│  │  • Booking Management Interface                           │   │
│  │  • Admin Dashboard                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        HTTPS / REST API
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND (REST API)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          API Layer (DRF ViewSets & APIViews)             │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ Authentication Endpoints  │  Booking Endpoints  │   │   │
│  │  │ • Token Obtain/Refresh    │  • List/Create      │   │   │
│  │  │ • Register/Login          │  • Retrieve/Update  │   │   │
│  │  │ • Password Reset          │  • Delete           │   │   │
│  │  │ • Admin Management        │                     │   │   │
│  │  │ • User Management         │                     │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        Business Logic & Serializers (DRF Layer)          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ Serializer Validation  │  Permission Checks      │   │   │
│  │  │ • Field Validation     │  • RBAC (Role-Based)    │   │   │
│  │  │ • Business Rules       │  • View-Level Checks    │   │   │
│  │  │ • Error Handling       │  • Serializer-Level     │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Database Models & ORM (Django ORM)            │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ User Models     │  Booking Models  │  Log Models │   │   │
│  │  │ • User          │  • Booking       │  • AdminAct │   │   │
│  │  │ • UserProfile   │                  │  • AcctHist │   │   │
│  │  │ • ResetToken    │                  │             │   │   │
│  │  │ • ResetAttempt  │                  │             │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    DATABASE / PERSISTENCE
                              ↓
        ┌───────────────────────────────────────┐
        │  PostgreSQL (Production / Render)     │
        │  SQLite (Development / Local)         │
        │                                       │
        │  • User & Profile Data                │
        │  • Booking Records                    │
        │  • Audit Logs                         │
        │  • Password Reset Tokens              │
        └───────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  SendGrid (Email Delivery)                             │    │
│  │  • Password Reset Emails                               │    │
│  │  • Account Notifications                               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Layer (React)
- **Technology**: React with HashRouter
- **Responsibilities**:
  - User interface for registration, login, password reset
  - Booking management interface
  - Admin dashboard
  - Token storage and management
  
**HashRouter Note:** Frontend uses HashRouter (`/#/`) for client-side routing, which is why password reset links must include the hash format.

---

### 2. API Layer (Django REST Framework)

#### Authentication App
**Location:** `authentication/`

**Endpoints:**
- User registration & authentication
- Password reset request/validation/confirmation
- Profile management
- Admin CRUD operations
- User management (admin only)
- Admin activity logging

**Key Components:**
- `views.py`: API endpoints (ViewSet & APIView classes)
- `serializers.py`: Input validation & transformation
- `models.py`: User, UserProfile, PasswordResetToken, AdminActivityLog, AccountHistory
- `urls.py`: URL routing
- `permissions.py`: Custom permission classes
- `utils.py`: Helper functions (token generation, email sending)

#### Booking App
**Location:** `booking/`

**Endpoints:**
- Booking CRUD operations (Create, Read, Update, Delete)
- Role-aware filtering (users see own bookings, admins see all)

**Key Components:**
- `views.py`: BookingViewSet using DRF's ModelViewSet
- `serializers.py`: Booking serialization with permission checks
- `models.py`: Booking model with status lifecycle
- `urls.py`: Automatic routing via SimpleRouter

---

### 3. Business Logic Layer

**Serializer Validation:**
- Email existence checks
- Password strength validation
- Status enforcement (regular users can't change booking status)
- Field transformations

**Permission System:**
- View-level: `permission_classes = (IsAuthenticated,)` or `(AllowAny,)`
- Serializer-level: Conditional field updates based on user role
- Queryset-level: Filter bookings by user

**Permission Matrix:**

| Model | Action | Regular User | Superuser |
|-------|--------|--------------|-----------|
| Booking | Create | Own only | Any user |
| Booking | Read | Own only | All |
| Booking | Update | Own (status reset to pending) | Any (all fields) |
| Booking | Delete | Own only | Any |
| User | Create | ❌ | ✅ |
| User | Reset Password | Self only | Any user |
| Admin | Manage | ❌ | ✅ |

---

### 4. Database Layer

**Technology Stack:**
- **ORM**: Django ORM
- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (via `DATABASE_URL`)

**Models:**

```
User (Django built-in)
├── UserProfile
│   ├── profile_picture (URLField)
│   ├── bio (TextField)
│   ├── memorable_information (TextField)
│   ├── can_revoke_admins (BooleanField)
│   └── timestamps (created_at, updated_at)
├── PasswordResetToken
│   ├── token (CharField, unique)
│   ├── created_at (DateTimeField)
│   ├── expires_at (DateTimeField, +1 hour)
│   └── is_used (BooleanField)
├── PasswordResetAttempt
│   ├── email (EmailField)
│   └── timestamp (DateTimeField)
├── AdminActivityLog
│   ├── admin (ForeignKey to User)
│   ├── action (CharField: CREATE_ADMIN, REVOKE_ADMIN, CREATE_USER, etc.)
│   ├── target_user (ForeignKey to User, nullable)
│   ├── description (TextField)
│   ├── ip_address (GenericIPAddressField)
│   └── timestamp (DateTimeField)
├── AccountHistory
│   ├── event_type (CharField: CREATED, REVOKED, RESTRICTED, UNRESTRICTED, PASSWORD_RESET)
│   ├── performed_by (ForeignKey to User, nullable)
│   ├── description (TextField)
│   ├── ip_address (GenericIPAddressField)
│   └── timestamp (DateTimeField)
└── Booking
    ├── booking_date (DateField)
    ├── booking_time (TimeField)
    ├── service_type (CharField)
    ├── status (CharField: pending, confirmed, completed, cancelled)
    ├── notes (TextField)
    └── timestamps (created_at, updated_at)
```

---

### 5. Security & Authentication

**JWT Flow:**

```
1. User sends credentials
   POST /api/auth/token/
   { "username": "john", "password": "pass" }
         ↓
2. Backend validates & issues tokens
   { "access": "...", "refresh": "..." }
         ↓
3. Client stores tokens (HttpOnly cookies / secure storage)
         ↓
4. Client includes access token in Authorization header
   GET /api/bookings/
   Authorization: Bearer eyJ...
         ↓
5. Backend validates token & processes request
         ↓
6. When access token expires, client uses refresh token
   POST /api/auth/token/refresh/
   { "refresh": "..." }
         ↓
7. Backend issues new access token
```

**Rate Limiting Flow:**

```
User requests password reset
   ↓
System checks PasswordResetAttempt table for email
   ↓
If count ≥ 3 in past 10 minutes:
   Return 429 with retry message
Else:
   Create attempt record
   Generate token
   Send email
   Return 200 OK
```

---

### 6. External Integrations

**SendGrid Email Service:**
- Password reset emails
- Account notification emails
- HTML templates with branded styling
- Error handling with graceful fallback

**Integration Points:**
```
Django Backend
     ↓
send_password_reset_email() [authentication/utils.py]
     ↓
SendGrid API (HTTPS)
     ↓
Email delivered to user inbox
```

---

## Data Flow Examples

### User Registration Flow

```
Frontend (Registration Form)
         ↓
POST /api/auth/register/
   { username, email, password, first_name, last_name, memorable_info }
         ↓
RegisterView (APIView)
   └─ RegisterSerializer.is_valid()
      └─ Check email doesn't exist
      └─ Validate password strength
         ↓
   └─ serializer.save()
      └─ User.objects.create_user()
      └─ Signal triggered: UserProfile auto-created
         ↓
Response: JWT tokens (access + refresh)
         ↓
Frontend: Store tokens, redirect to dashboard
```

---

### Password Reset Flow

```
Frontend (Forgot Password Form)
         ↓
POST /api/auth/password-reset/request/
   { email: "user@example.com" }
         ↓
RequestPasswordResetView
   ├─ Check rate limiting (3 attempts per 10 min)
   ├─ Create PasswordResetAttempt record
   ├─ Generate secure token
   ├─ Create PasswordResetToken (expires in 1 hour)
   └─ send_password_reset_email()
         ↓
SendGrid
   └─ Deliver email with reset link
         ↓
Frontend: User clicks link in email
   └─ Redirects to /#/reset-password?token=ABC123
         ↓
Frontend: Display reset form
   └─ User enters new password
         ↓
POST /api/auth/password-reset/confirm/
   { token: "ABC123", new_password: "NewPass456!" }
         ↓
ResetPasswordView
   ├─ Validate token exists & not expired & not used
   ├─ Update user.set_password()
   ├─ Mark token as is_used = True
   └─ Log event in AccountHistory
         ↓
Response: 200 OK
         ↓
Frontend: Redirect to login
```

---

### Booking Creation Flow (Admin)

```
Admin Dashboard
         ↓
POST /api/bookings/
   Authorization: Bearer <admin_token>
   { user_id: 5, booking_date: "2026-04-15", ... }
         ↓
BookingViewSet.create()
   ├─ Check permission: IsAuthenticated + is_superuser
   ├─ BookingSerializer.is_valid()
   │  └─ Admin can set any status
   └─ Booking.objects.create()
         ↓
Response: 201 Created with booking details
         ↓
Database: Booking record stored
         ↓
Frontend: Display confirmation
```

### Booking Retrieval Flow (Regular User)

```
User Dashboard
         ↓
GET /api/bookings/
   Authorization: Bearer <user_token>
         ↓
BookingViewSet.list()
   ├─ Check permission: IsAuthenticated
   ├─ Filter queryset: bookings where user_id = request.user.id
   └─ Return only user's own bookings
         ↓
Response: 200 OK with user's bookings
         ↓
Frontend: Display user's bookings only
```

---

## Deployment Architecture

### Development
- **Server**: Django development server (`python manage.py runserver`)
- **Database**: SQLite (file-based)
- **Frontend**: React dev server
- **Environment**: Local machine

### Production (Render)
```
Render Platform
├─ Web Service (Backend)
│  ├─ Python runtime
│  ├─ Gunicorn WSGI server (4 workers)
│  ├─ WhiteNoise static file serving
│  └─ Environment variables (secrets)
└─ PostgreSQL Database
   ├─ Managed database service
   ├─ Automatic backups
   └─ Connection pooling
```

**Load Balancing**: Render provides automatic load balancing across Gunicorn workers.

---

## Security Architecture

### Authentication
- JWT tokens (djangorestframework-simplejwt)
- Short-lived access tokens (5 minutes default)
- Refresh tokens for obtaining new access tokens
- HttpOnly cookies or secure local storage on frontend

### Authorization
- Role-Based Access Control (RBAC)
- Superuser flag for admins
- View-level permission checks
- Serializer-level field-access restrictions
- Queryset-level data filtering

### Data Protection
- Environment variables for secrets (no hardcoding)
- CSRF/CORS protection
- Password hashing with PBKDF2 + salt
- Password strength validation
- Token expiration & single-use enforcement
- IP address logging for audit trail

### Rate Limiting
- Password reset: 3 attempts per 10 minutes
- Prevents brute force attacks
- Returns helpful retry information

---

## Modularity & Extensibility

**Apps can be deployed independently:**
- `authentication` app could be extracted to separate service
- `booking` app could be enhanced with notifications, calendar integration
- Easy to add new apps (e.g., `payments`, `scheduling`)

**Future Enhancement Points:**
- Add email notification service (Django Celery)
- Add real-time updates (WebSockets)
- Add API versioning (DRF versioning)
- Add pagination (already configured)
- Add OpenAPI schema generation (drf-spectacular)
- Add Redis caching layer
- Add ElasticSearch for advanced search

---

## Performance Considerations

1. **Database Queries**: Use `.select_related()` and `.prefetch_related()` for optimized queries
2. **Caching**: Can add Redis caching for frequently accessed data
3. **API Pagination**: Implemented for list endpoints to prevent returning large datasets
4. **Static Files**: WhiteNoise for efficient serving in production
5. **Gunicorn Workers**: Configured for concurrent request handling
6. **Connection Pooling**: PostgreSQL handles connection pooling in production

---

## Monitoring & Logging

**Currently Implemented:**
- AdminActivityLog: All admin actions logged with timestamp and IP
- AccountHistory: User account events logged
- Django logging: Available for enabled apps

**Future Enhancements:**
- Centralized logging (Sentry)
- Performance monitoring (New Relic, DataDog)
- Application health checks
- Database query monitoring
- API response time tracking

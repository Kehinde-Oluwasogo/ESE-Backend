# ESE Booking System Backend API

Backend service for booking management, authentication, and admin operations, built with Django and Django REST Framework.

## Overview

This repository contains the API layer for the ESE booking system. It includes:

- JWT authentication
- User registration and profile retrieval
- Password reset flow with token validation
- Super-admin user and admin management endpoints
- Booking CRUD endpoints with role-aware behavior
- Admin and account activity logging

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SendGrid (email delivery)
- SQLite (default) or PostgreSQL via DATABASE_URL
- Gunicorn + WhiteNoise (production serving)

Dependencies are listed in [requirements.txt](requirements.txt).

## Project Structure

- [backend](backend): Django project settings and root URL configuration
- [authentication](authentication): auth, password reset, admin/user management, logging
- [booking](booking): booking model, serializer, and viewset
- [manage.py](manage.py): Django management entrypoint
- [build.sh](build.sh): build/deploy helper script

## Setup

1. Clone repository and move into project directory.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create environment variables (see next section).
5. Apply migrations:

```bash
python manage.py migrate
```

6. Create admin user (optional, recommended):

```bash
python manage.py createsuperuser
```

7. Start development server:

```bash
python manage.py runserver
```

API is available at http://localhost:8000.

## Environment Variables

Create a .env file at project root (same level as [manage.py](manage.py)).

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@example.com
# Optional alias used by settings
FROM_EMAIL=noreply@example.com

# URL used to build password reset links in email
FRONTEND_URL=http://localhost:3000

# CORS / CSRF (mainly for non-debug or hosted clients)
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```

## API Routes

Base root:

- /admin/
- /api/
- /api/auth/

Authentication routes are defined in [authentication/urls.py](authentication/urls.py).

### Public Authentication Endpoints

- POST /api/auth/token/
- POST /api/auth/token/refresh/
- POST /api/auth/register/
- POST /api/auth/password-reset/request/
- POST /api/auth/password-reset/validate/
- POST /api/auth/password-reset/confirm/

### Authenticated User Endpoints

- GET /api/auth/user/
- POST /api/auth/profile/picture/

### Super Admin Endpoints

- POST /api/auth/admin/create/
- GET /api/auth/admin/list/
- POST /api/auth/admin/revoke/
- GET /api/auth/admin/activity-logs/
- GET /api/auth/users/list/
- POST /api/auth/users/create/
- POST /api/auth/users/change-password/
- POST /api/auth/users/send-reset-link/
- POST /api/auth/users/toggle-active/

### Booking Endpoints

The bookings API is provided by a DRF router in [backend/urls.py](backend/urls.py):

- GET /api/bookings/
- POST /api/bookings/
- GET /api/bookings/{id}/
- PUT /api/bookings/{id}/
- PATCH /api/bookings/{id}/
- DELETE /api/bookings/{id}/

Behavior summary:

- Regular users only see and manage their own bookings.
- Super admins can view all bookings.
- Super admins may create bookings for another user by passing user_id.

## Data Model Summary

Core models are defined in [authentication/models.py](authentication/models.py) and [booking/models.py](booking/models.py):

- UserProfile
- PasswordResetToken
- PasswordResetAttempt
- AdminActivityLog
- AccountHistory
- Booking

## Production Notes

- Build helper script: [build.sh](build.sh)
- Typical production start command:

```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

- Static files are collected to staticfiles and served with WhiteNoise.
- Set DEBUG=False and configure ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, and CSRF_TRUSTED_ORIGINS appropriately.

## Current Testing Status

No automated test files are currently present in this repository.

## Author

- Kehinde Oluwasogo
- GitHub: https://github.com/KehindeOluwasogo-BC
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from authentication.models import AccountHistory, PasswordResetAttempt


pytestmark = pytest.mark.django_db


def test_rate_limit_triggers_after_three_recent_attempts():
    email = "rate-limit@example.com"

    for _ in range(3):
        PasswordResetAttempt.objects.create(email=email)

    is_limited, seconds_remaining = PasswordResetAttempt.is_rate_limited(email)

    assert is_limited is True
    assert 0 < seconds_remaining <= 600


def test_register_endpoint_creates_user_profile_and_returns_tokens():
    client = APIClient()
    payload = {
        "username": "integration_user",
        "email": "integration_user@example.com",
        "password": "StrongPass123!",
        "first_name": "Integration",
        "last_name": "User",
        "memorable_information": "first-school",
    }

    response = client.post("/api/auth/register/", payload, format="json")

    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data

    user = User.objects.get(username=payload["username"])
    assert hasattr(user, "profile")
    assert user.profile.memorable_information == payload["memorable_information"]

    history = AccountHistory.objects.get(user=user)
    assert history.event_type == "CREATED"


def test_password_reset_request_returns_429_when_rate_limited():
    user = User.objects.create_user(
        username="reset_target",
        email="reset_target@example.com",
        password="StrongPass123!",
    )

    for _ in range(3):
        PasswordResetAttempt.objects.create(email=user.email)

    client = APIClient()
    response = client.post(
        "/api/auth/password-reset/request/",
        {"email": user.email},
        format="json",
    )

    assert response.status_code == 429
    assert response.data["rate_limited"] is True
    assert "retry_message" in response.data

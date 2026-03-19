from datetime import date, time
from types import SimpleNamespace

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from booking.models import Booking
from booking.serializers import BookingSerializer


pytestmark = pytest.mark.django_db


def test_regular_user_update_forces_non_pending_status_back_to_pending():
    user = User.objects.create_user(username="booking_unit_user", password="StrongPass123!")
    booking = Booking.objects.create(
        user=user,
        full_name="Unit User",
        email="unit@example.com",
        service="Haircut",
        booking_date=date(2026, 3, 11),
        booking_time=time(9, 0),
        notes="initial",
        status="confirmed",
    )

    request = SimpleNamespace(user=user)

    serializer = BookingSerializer(
        instance=booking,
        data={"status": "cancelled", "notes": "updated by regular user"},
        partial=True,
        context={"request": request},
    )
    assert serializer.is_valid(), serializer.errors

    updated_booking = serializer.save()

    assert updated_booking.notes == "updated by regular user"
    assert updated_booking.status == "pending"


def test_superuser_can_create_booking_for_target_user_with_user_id():
    admin = User.objects.create_superuser(
        username="booking_admin",
        email="booking_admin@example.com",
        password="StrongPass123!",
    )
    target_user = User.objects.create_user(
        username="booking_target",
        email="booking_target@example.com",
        password="StrongPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    payload = {
        "full_name": "Target User",
        "email": "booking_target@example.com",
        "service": "Massage",
        "booking_date": date(2026, 3, 13).isoformat(),
        "booking_time": time(14, 0).isoformat(),
        "notes": "admin-created booking",
        "status": "pending",
        "user_id": target_user.id,
    }

    response = client.post("/api/bookings/", payload, format="json")

    assert response.status_code == 201

    created_booking = Booking.objects.get(id=response.data["id"])
    assert created_booking.user_id == target_user.id
    assert created_booking.full_name == payload["full_name"]

import pytest
from django.contrib.auth.models import User
from pytest_bdd import given, scenario, then, when
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


@scenario("features/auth_user_info.feature", "Retrieve current authenticated user profile")
def test_retrieve_current_authenticated_user_profile():
    pass


@given("an existing registered user", target_fixture="auth_user")
def auth_user():
    return User.objects.create_user(
        username="auth_bdd_user",
        email="auth_bdd_user@example.com",
        password="StrongPass123!",
        first_name="Auth",
        last_name="BDD",
    )


@given("the user is authenticated with the API client", target_fixture="api_client")
def api_client(auth_user):
    client = APIClient()
    client.force_authenticate(user=auth_user)
    return client


@when("the user requests the authentication profile endpoint", target_fixture="response")
def request_profile(api_client):
    return api_client.get("/api/auth/user/")


@then("the response status code is 200")
def assert_status_ok(response):
    assert response.status_code == 200


@then("the response includes the authenticated username")
def assert_username(response, auth_user):
    assert response.data["username"] == auth_user.username

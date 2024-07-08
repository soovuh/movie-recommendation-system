import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture()
def user():
    user = User.objects.create(username="test", email="test@example.com")
    user.set_password("testpassword123")
    user.save()
    return user


@pytest.fixture()
def api_client():
    return APIClient()

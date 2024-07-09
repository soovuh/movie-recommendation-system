import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Movie


User = get_user_model()


@pytest.fixture()
def user():
    user = User.objects.create(username="test", email="test@example.com")
    user.set_password("testpassword123")
    user.save()
    return user


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", password="adminpass", email="admin@example.com"
    )


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def movie(db):
    return Movie.objects.create(
        title="Inception",
        genre="Sci-Fi",
        description="A mind-bending thriller",
        release_date="2010-07-16",
    )


@pytest.fixture
def movie_data():
    return {
        "title": "Inception",
        "genre": "Sci-Fi",
        "description": "A mind-bending thriller",
        "release_date": "2010-07-16",
    }

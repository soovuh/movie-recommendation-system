import pytest
from django.urls import reverse

from core.models import Rating


@pytest.mark.django_db
class TestMovieViewSet:
    def test_get_movie_list(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_get_single_movie(self, api_client, admin_user, movie):
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-detail", args=[movie.id])
        response = api_client.get(url)
        assert response.status_code == 200

    def test_create_movie(self, api_client, admin_user, movie_data):
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-list")
        response = api_client.post(url, data=movie_data, format="json")
        assert response.status_code == 201

    def test_update_movie(self, api_client, admin_user, movie, movie_data):
        movie_data["title"] = "Inception Updated"
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-detail", args=[movie.id])
        response = api_client.put(url, data=movie_data, format="json")
        assert response.status_code == 200

    def test_delete_movie(self, api_client, admin_user, movie):
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-detail", args=[movie.id])
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_user_cannot_create_movie(self, api_client, user, movie_data):
        api_client.force_authenticate(user=user)
        url = reverse("movie-list")
        response = api_client.post(url, data=movie_data, format="json")
        assert response.status_code == 403

    def test_user_cannot_update_movie(self, api_client, user, movie, movie_data):
        movie_data["title"] = "Inception Updated"
        api_client.force_authenticate(user=user)
        url = reverse("movie-detail", args=[movie.id])
        response = api_client.put(url, data=movie_data, format="json")
        assert response.status_code == 403

    def test_user_cannot_delete_movie(self, api_client, user, movie):
        api_client.force_authenticate(user=user)
        url = reverse("movie-detail", args=[movie.id])
        response = api_client.delete(url)
        assert response.status_code == 403

    def test_get_ratings(self, api_client, admin_user, user, movie):
        Rating.objects.create(user=admin_user, movie=movie, rating=8.0)
        Rating.objects.create(user=user, movie=movie, rating=7.5)

        movie.refresh_from_db()
        assert movie.general_rating == 7.75

        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-get-ratings", args=[movie.id])
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_create_rating(self, api_client, user, movie):
        api_client.force_authenticate(user=user)

        rating_data = {"rating": 9.0}
        url = reverse("movie-create-rating", args=[movie.id])
        response = api_client.post(url, data=rating_data, format="json")

        assert response.status_code == 201
        assert Rating.objects.filter(user=user, movie=movie, rating=9.0).exists()

    def test_create_duplicate_rating(self, api_client, user, movie):
        Rating.objects.create(user=user, movie=movie, rating=8.0)

        api_client.force_authenticate(user=user)

        rating_data = {"rating": 8.0}
        url = reverse("movie-create-rating", args=[movie.id])
        response = api_client.post(url, data=rating_data, format="json")

        assert response.status_code == 400
        assert response.data["error"] == "You have already rated this movie."

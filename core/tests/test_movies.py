import pytest
from django.urls import reverse


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

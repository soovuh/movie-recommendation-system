import pytest
from django.urls import reverse
from django.utils import timezone

from core.models import Rating, MovieViewingHistory, Movie


@pytest.mark.django_db
class TestMovieViewSet:
    def test_get_movie_list(self, api_client, admin_user, movie):
        api_client.force_authenticate(user=admin_user)
        url = reverse("movie-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

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

    def test_movie_viewing_history_created(self, api_client, user, movie):
        api_client.force_authenticate(user=user)

        url = reverse("movie-detail", args=[movie.id])
        response = api_client.get(url)

        assert response.status_code == 200
        assert MovieViewingHistory.objects.get(user=user, movie=movie) is not None


@pytest.mark.django_db
class TestMovieFilters:
    def test_filter_movies_by_genre(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        Movie.objects.create(
            title="Comedy Movie",
            genre="Comedy",
            description="A funny movie.",
            release_date=timezone.now(),
        )
        Movie.objects.create(
            title="Drama Movie",
            genre="Drama",
            description="A dramatic movie.",
            release_date=timezone.now(),
        )
        url = reverse("movie-list")
        response = api_client.get(url, {"genre": "Comedy"})
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["genre"] == "Comedy"

    def test_search_movies_by_title(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        Movie.objects.create(
            title="Unique Title",
            genre="Action",
            description="An action movie.",
            release_date=timezone.now(),
        )
        Movie.objects.create(
            title="Another Title",
            genre="Action",
            description="Another action movie.",
            release_date=timezone.now(),
        )
        url = reverse("movie-list")
        response = api_client.get(url, {"search": "Unique Title"})
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Unique Title"

    def test_pagination(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        for i in range(15):
            Movie.objects.create(
                title=f"Movie {i}",
                genre="Action",
                description="An action movie.",
                release_date=timezone.now(),
            )
        url = reverse("movie-list")
        response = api_client.get(url, {"page": 2, "page_size": 10})
        assert response.status_code == 200
        assert len(response.data["results"]) == 5
        assert response.data["count"] == 15
        assert response.data["next"] is None
        assert response.data["previous"] is not None

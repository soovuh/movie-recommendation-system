import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse


@pytest.mark.django_db
class TestUserAuth:
    def test_user_create(self, api_client):
        data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "testemail@example.com",
        }
        url = reverse("register")
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == 201

    @patch("rest_framework.authtoken.models.Token.objects.get_or_create")
    def test_user_login(self, mock_get_or_create, api_client, user):
        mock_token = MagicMock()
        mock_token.key = "mocked_token_key"
        mock_get_or_create.return_value = (mock_token, True)

        data = {"username": user.username, "password": "testpassword123"}
        url = reverse("login")
        response = api_client.post(url, data=data, format="json")

        assert response.status_code == 200
        assert response.data["token"] == "mocked_token_key"
        mock_get_or_create.assert_called_once()

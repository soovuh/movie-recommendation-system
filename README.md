# Movie Recommendation System

## Description

This project is a Django REST Framework (DRF) based API that provides movie recommendations to users. The system includes functionalities for user registration, login, viewing movie details, rating movies, and generating personalized movie recommendations.

## Stack

- Django
- DRF
- Pandas

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/soovuh/movie-recommendation-system.git
    cd movie-recommendation-system
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

5. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## Endpoints

**Note:** After login, you will receive a token. Use this token for all subsequent requests by setting the `Authorization` header as `Token <token>`.

### User Registration

- **Endpoint:** `api/register/`
- **Method:** `POST`
- **Parameters:**
    - `username`: string
    - `email`: string
    - `password`: string

### User Login

- **Endpoint:** `api/login/`
- **Method:** `POST`
- **Parameters:**
    - `username`: string
    - `password`: string

### Movie List and Details

- **Endpoint:** `api/movies/`
- **Method:** `GET`
- **Parameters:** 
    - **Filtering:** `genre`, `release_date`, `general_rating`
    - **Search:** `title`, `description`

**Note:** This endpoint has pagination.

### Retrieve a Movie's Details

- **Endpoint:** `api/movies/<id>/`
- **Method:** `GET`
- **Parameters:** None

### Create Movie Rating

- **Endpoint:** `api/movies/<id>/ratings/create/`
- **Method:** `POST`
- **Parameters:**
    - `rating`: float (1-10)
    - `review`: string (optional)

### Get Movie Ratings for Movie

- **Endpoint:** `api/movies/<movie_id>/ratings/`
- **Method:** `GET`
- **Parameters:** None

### Get Recommendations

- **Endpoint:** `api/recommendations/`
- **Method:** `GET`
- **Parameters:** None

**Note:** This endpoint has pagination.

### Admin-only Endpoints

Only admin users can create, update, or delete movies.

### Create Movie
- **Endpoint:** `api/movies/`
- **Method:** `POST`
- **Parameters:**
    - `title`: string (max_length=255)
    - `genre`: string (max_length=255)
    - `description`: text
    - `release_date`: date
    - `general_rating`: float (1 - 10)
    - `review`: string (optional)

### Update Movie
- **Endpoint:** `api/movies/<id>/`
- **Method:** `PUT`
- **Parameters:** Various fields for movie details.

### Delete Movie
- **Endpoint:** `api/movies/<id>/`
- **Method:** `DELETE`
- **Parameters:** None

## Project Structure

### `core/`

- **`admin.py`**: Registers models with the admin site.
- **`apps.py`**: Application configuration.
- **`models.py`**: Defines the database models:
  - `User`: User model (extended from Django's default user).
  - `Movie`: Movie model with fields like title, genre, description, release date, and general rating.
  - `Rating`: Rating model to store user ratings for movies.
  - `MovieViewingHistory`: Model to track the movies viewed by users.
- **`urls.py`**: Routes URLs to the appropriate views.
- **`views.py`**: Implements the API views:
  - `UserRegistrationView`: Handles user registration.
  - `UserLoginView`: Handles user login and token generation.
  - `MovieViewSet`: Handles CRUD operations for movies, movie ratings, and viewing history.
  - `MovieRecommendationView`: Provides movie recommendations to authenticated users.
- **`api/`**: Contains serializers, permissions, filters, and pagination for the API:
  - `serializers.py`: Serializes and deserializes data.
  - `permissions.py`: Custom permissions for the API.
  - `filters.py`: Defines filters for the API views.
  - `pagination.py`: Custom pagination settings.
- **`utils/recommendation.py`**: Implements the recommendation algorithm with Pandas.

### `movie_recommendation_system/`

- **`settings.py`**: Django settings for the project.
- **`urls.py`**: Main URL configurations.
- **`asgi.py`**: ASGI application configuration.
- **`wsgi.py`**: WSGI application configuration.

## Development and Testing

1. **Install the development dependencies:**
    ```bash
    pip install -r requirements_dev.txt
    ```

2. **Run the tests:**
    ```bash
    pytest
    ```

Tests are located in the `core/tests/` directory.
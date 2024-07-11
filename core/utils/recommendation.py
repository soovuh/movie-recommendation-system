import pandas as pd
from django.db.models import Avg
import logging
from core.models import Rating, MovieViewingHistory

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_data(queryset, columns):
    df = pd.DataFrame(list(queryset))
    if df.empty:
        df = pd.DataFrame(columns=columns)
    logger.debug(f"Data retrieved: {df}")
    return df


def get_viewing_history(user):
    history = MovieViewingHistory.objects.filter(user=user).values(
        "movie__id", "movie__title", "movie__genre"
    )
    return get_data(history, ["movie__id", "movie__title", "movie__genre"])


def get_user_ratings(user):
    ratings = Rating.objects.filter(user=user).values(
        "movie__id", "movie__title", "movie__genre", "rating"
    )
    return get_data(ratings, ["movie__id", "movie__title", "movie__genre", "rating"])


def get_global_ratings():
    ratings = Rating.objects.values(
        "movie__id", "movie__title", "movie__genre"
    ).annotate(avg_rating=Avg("rating"))
    return get_data(
        ratings, ["movie__id", "movie__title", "movie__genre", "avg_rating"]
    )


def filter_movies(viewed_movies, user_ratings, global_ratings):
    if not viewed_movies.empty:
        viewed_movie_ids = viewed_movies["movie__id"].unique()
        global_ratings = global_ratings[
            ~global_ratings["movie__id"].isin(viewed_movie_ids)
        ]

    if not user_ratings.empty:
        low_rated_movie_ids = user_ratings[user_ratings["rating"] <= 2][
            "movie__id"
        ].unique()
        global_ratings = global_ratings[
            ~global_ratings["movie__id"].isin(low_rated_movie_ids)
        ]

    return global_ratings


def sort_movies_by_rating(movies):
    sorted_movies = movies.sort_values(by=["avg_rating"], ascending=False)
    logger.debug(f"Movies sorted by rating: {sorted_movies}")
    return sorted_movies


def sort_movies_by_genre_similarity(movies, user_genre_preference):
    movies["genre_similarity"] = movies["movie__genre"].apply(
        lambda genre: genre == user_genre_preference
    )
    sorted_movies = movies.sort_values(
        by=["genre_similarity", "avg_rating"], ascending=[False, False]
    )
    logger.debug(f"Movies sorted by genre similarity: {sorted_movies}")
    return sorted_movies


def recommend_movies(user):
    viewed_movies = get_viewing_history(user)
    user_ratings = get_user_ratings(user)
    global_ratings = get_global_ratings()

    filtered_movies = filter_movies(viewed_movies, user_ratings, global_ratings)

    recommended_movies = sort_movies_by_rating(filtered_movies)

    if not viewed_movies.empty:
        user_genre_preference = viewed_movies["movie__genre"].mode()[0]
        recommended_movies = sort_movies_by_genre_similarity(
            recommended_movies, user_genre_preference
        )

    logger.debug(f"Final recommended movies: {recommended_movies}")
    return recommended_movies.head(10).to_dict("records")


def generate_recommendations(user):
    recommendations = recommend_movies(user)
    logger.debug(f"Generated recommendations: {recommendations}")
    return recommendations

import pandas as pd
from core.models import Movie, Rating, MovieViewingHistory


def get_data(queryset, columns):
    df = pd.DataFrame(list(queryset))
    if df.empty:
        df = pd.DataFrame(columns=columns)
    return df


def get_viewing_and_ratings(user):
    viewing_history = MovieViewingHistory.objects.filter(user=user).values(
        "movie__id", "movie__title", "movie__genre"
    )
    user_ratings = Rating.objects.filter(user=user).values(
        "movie__id", "movie__title", "movie__genre", "rating"
    )
    viewing_df = get_data(
        viewing_history, ["movie__id", "movie__title", "movie__genre"]
    )
    ratings_df = get_data(
        user_ratings, ["movie__id", "movie__title", "movie__genre", "rating"]
    )
    return viewing_df, ratings_df


def get_global_ratings():
    movies = Movie.objects.values("id", "title", "genre", "general_rating").filter(
        general_rating__gt=5.0
    )
    return get_data(movies, ["id", "title", "genre", "general_rating"])


def filter_movies(viewed_movies, user_ratings, global_ratings):
    if not viewed_movies.empty:
        viewed_movie_ids = viewed_movies["movie__id"].unique()
        global_ratings = global_ratings[~global_ratings["id"].isin(viewed_movie_ids)]

    if not user_ratings.empty:
        low_rated_movie_ids = user_ratings[user_ratings["rating"] <= 5][
            "movie__id"
        ].unique()
        global_ratings = global_ratings[~global_ratings["id"].isin(low_rated_movie_ids)]

    return global_ratings


def sort_movies_by_rating(movies):
    return movies.sort_values(by=["general_rating"], ascending=False)


def get_user_genre_preference(user_ratings):
    good_ratings = user_ratings[user_ratings["rating"] > 5]
    low_rated_genres = user_ratings[user_ratings["rating"] <= 2][
        "movie__genre"
    ].unique()
    if not good_ratings.empty:
        preferred_genres = good_ratings["movie__genre"].mode()
        if not preferred_genres.empty:
            return preferred_genres[0], low_rated_genres
    return None, low_rated_genres


def sort_movies_by_genre_similarity(movies, user_genre_preference):
    movies["genre_similarity"] = movies["genre"].apply(
        lambda genre: genre == user_genre_preference
    )
    return movies.sort_values(
        by=["genre_similarity", "general_rating"], ascending=[False, False]
    )


def recommend_movies(user):
    viewed_movies, user_ratings = get_viewing_and_ratings(user)
    global_ratings = get_global_ratings()

    filtered_movies = filter_movies(viewed_movies, user_ratings, global_ratings)
    sorted_by_rating = sort_movies_by_rating(filtered_movies)

    user_genre_preference, low_rated_genres = get_user_genre_preference(user_ratings)
    if user_genre_preference:
        sorted_by_rating = sort_movies_by_genre_similarity(
            sorted_by_rating, user_genre_preference
        )
    sorted_by_rating = sorted_by_rating[
        ~sorted_by_rating["genre"].isin(low_rated_genres)
    ]

    return sorted_by_rating


def refine_recommendations(recommendations, user):
    if recommendations.empty:
        return []

    _, user_ratings = get_viewing_and_ratings(user)
    user_genre_preference, _ = get_user_genre_preference(user_ratings)
    genre_freq = user_ratings["movie__genre"].value_counts(normalize=True)

    recommendations["weighted_score"] = recommendations.apply(
        lambda row: row["general_rating"]
        * (1.5 if row["genre"] == user_genre_preference else 1)
        * (genre_freq.get(row["genre"], 0.1) + 1),
        axis=1,
    )
    recommendations = recommendations.sort_values(
        by=["weighted_score"], ascending=False
    )
    return recommendations.to_dict("records")


def generate_recommendations(user):
    recommendations = recommend_movies(user)
    return refine_recommendations(recommendations, user)

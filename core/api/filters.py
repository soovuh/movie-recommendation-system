from django_filters import rest_framework as filters

from core.models import Movie


class MovieFilter(filters.FilterSet):
    class Meta:
        model = Movie
        fields = ["genre", "release_date", "general_rating"]

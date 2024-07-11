from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from core.api import serializers
from core.models import Movie, Rating, MovieViewingHistory
from core.api.permissions import IsAdminOrReadOnly
from core.api.filters import MovieFilter
from core.utils.recommendation import generate_recommendations
from core.api.pagination import CustomPageNumberPagination


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = authenticate(
            username=request.data["username"], password=request.data["password"]
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Invalid credentials"}, status=401)


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = serializers.MovieSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = MovieFilter
    search_fields = ("title", "description")
    pagination_class = CustomPageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        already_viewed = MovieViewingHistory.objects.filter(
            user=user, movie=instance
        ).first()
        if not already_viewed:
            MovieViewingHistory.objects.create(user=user, movie=instance)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="ratings",
    )
    def get_ratings(self, request, pk=None):
        movie = self.get_object()
        ratings = Rating.objects.filter(movie=movie)
        serializer = serializers.RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="ratings/create",
    )
    def create_rating(self, request, pk=None):
        movie = self.get_object()
        user = request.user

        existing_rating = Rating.objects.filter(user=user, movie=movie).first()
        if existing_rating:
            return Response({"error": "You have already rated this movie."}, status=400)

        serializer = serializers.RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, movie=movie)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class MovieRecommendationView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class = serializers.MovieRecommendationSerializer

    def get_queryset(self):
        user = self.request.user
        recommendations = generate_recommendations(user)
        return recommendations

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

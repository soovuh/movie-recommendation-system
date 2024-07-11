from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()
router.register(r"movies", views.MovieViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path(
        "recommendations/",
        views.MovieRecommendationView.as_view(),
        name="recommendations",
    ),
]

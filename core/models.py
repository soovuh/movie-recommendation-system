from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.release_date.year}"

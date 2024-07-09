from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    general_rating = models.FloatField(default=0.0)

    def update_general_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            self.general_rating = ratings.aggregate(models.Avg("rating"))["rating__avg"]
            self.save()

    def __str__(self):
        return f"{self.title} - {self.release_date.year}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name="ratings", on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.movie.update_general_rating()

# Generated by Django 5.0.6 on 2024-07-09 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_rating"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="general_rating",
            field=models.FloatField(default=0.0),
        ),
    ]

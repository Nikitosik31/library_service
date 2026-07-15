from django.db import models
from django.db.models import TextChoices


class CoverType(TextChoices):
    HARD = "Hard"
    SOFT = "Soft"


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=200, choices=CoverType.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Name {self.title}, Author {self.author}"

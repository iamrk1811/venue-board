from django.db import models
from core.models import TimeStampedModel
from .const import VenueTypes


class Venue(TimeStampedModel):
    name = models.CharField(max_length=200)
    type = models.IntegerField(choices=VenueTypes.TYPES)
    location = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

import datetime
import uuid
from datetime import timezone

from django.db import models


class User(models.Model):  # id field is added automatically
    _id = models.TextField(primary_key=True, default="", editable=False, unique=True)
    name = models.CharField(max_length=60)

    def __str__(self):  # toString()
        return (self.name)

class Map(models.Model):
    _id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # name of the Map
    # theme of the Map, ex: Bear Sightings Around the World
    description = models.CharField(max_length=50)

    def __str__(self):
        return ('Map: {0}, Description: {1}'.format(self.name, self.description))


class Note(models.Model):
    _id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    map_container = models.ForeignKey(Map, on_delete=models.CASCADE)

    body = models.TextField(max_length=500)
    date = models.DateTimeField('date published')
    upvotes = models.IntegerField(default=0)

    lat = models.DecimalField(max_digits=30, decimal_places=25)
    lon = models.DecimalField(max_digits=30, decimal_places=25)

    def __str__(self):
        return ("|{0}| {1} wrote in map {2}: \'{3}\'. +{4} votes".format(self.date, self.creator,
                                                                         self.map_container, self.body, self.upvotes))

    def get_creator_name(self):
        return self.creator.name

    # Returns true if note was published less than or equal to a day from now
    def was_published_recently(self):
        return self.date >= timezone.now() - datetime.timedelta(days=1)

from django.db import models
from restroom import expose


class MyModel(models.Model):
    name = models.CharField(max_length=150)


@expose(fields=['short_title', 'author'])
class ExposedModelToSerialize(models.Model):
    short_title = models.CharField(max_length=150)
    expired = models.BooleanField(default=False)
    author = models.CharField(max_length=120)
    status = models.IntegerField(default=1)

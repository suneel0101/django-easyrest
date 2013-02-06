from django.db import models
from restroom import expose, API


class MyModel(models.Model):
    name = models.CharField(max_length=150)

exposed_model_to_serialize_api = API()


@expose(api=exposed_model_to_serialize_api,
        fields=['short_title', 'author'])
class ExposedModelToSerialize(models.Model):
    short_title = models.CharField(max_length=150)
    expired = models.BooleanField(default=False)
    author = models.CharField(max_length=120)
    status = models.IntegerField(default=1)

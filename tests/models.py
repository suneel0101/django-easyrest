from django.db import models
from restroom import expose, API


@expose(fields=['text', 'expired', 'id'],
        allowed_methods=['GET', 'POST', 'DELETE', 'PUT'],
        per_page=5)
class CrazyModel(models.Model):
    text = models.CharField(max_length=150)
    expired = models.BooleanField(default=False)
    title = models.CharField(max_length=150)


class MyModel(models.Model):
    name = models.CharField(max_length=150)

exposed_model_to_serialize_api = API()


@expose(api=exposed_model_to_serialize_api,
        fields=['short_title', 'author', 'id'])
class ExposedModelToSerialize(models.Model):
    short_title = models.CharField(max_length=150)
    expired = models.BooleanField(default=False)
    author = models.CharField(max_length=120)
    status = models.IntegerField(default=1)

another_test_api = API()


@expose(api=another_test_api,
        fields=['text', 'slug', 'id', 'active'])
class AnotherModel(models.Model):
    text = models.CharField(null=False, blank=False, max_length=50)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(blank=False)


test_api = API()


@expose(api=test_api, fields=['awesome', 'slogan', 'id'])
class ExposedFK(models.Model):
    slug = models.SlugField()
    awesome = models.BooleanField(default=True)
    slogan = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)


class MyFK(models.Model):
    active = models.BooleanField()
    name = models.CharField(max_length=150)
    exposed_fk = models.ForeignKey('tests.ExposedFK')


@expose(api=test_api,
        fields=['text', 'id', 'my_fk'])
class ModelWithFK(models.Model):
    text = models.CharField(null=False, blank=False, max_length=50)
    my_fk = models.ForeignKey('tests.MyFK')


test_datetime_api = API()


@expose(api=test_datetime_api, fields=['timestamp', 'id'])
class DateTimeModel(models.Model):
    timestamp = models.DateTimeField()
    text = models.CharField(max_length=150)


paginated_api = API()


@expose(api=paginated_api,
        fields=['text', 'slug', 'id'],
        per_page=50)
class PaginatedModel(models.Model):
    text = models.CharField(null=False, blank=False, max_length=50)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(blank=False)


class Modelo(models.Model):
    text = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)

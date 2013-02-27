from django.db import models


class Modelo(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)

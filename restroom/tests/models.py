import datetime
from django.db import models


class Modelo(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)


class Modela(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)


class Modelb(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now())
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)


class Modelc(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)


class ModelAuthed(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)


class ModelfkUser(models.Model):
    text = models.CharField(max_length=250, blank=False)
    slug = models.SlugField(unique=True)
    awesome = models.BooleanField()
    optional_text = models.CharField(max_length=300)
    owner = models.ForeignKey('auth.user')

from django.db import models
from django.contrib.auth.models import User


class APIKey(models.Model):
    token = models.CharField(unique=True, max_length=16)
    user = models.ForeignKey('auth.user')

    def save(self, *args, **kwargs):
        # Generate unique token
        if not self.token:
            unique = False
            while not unique:
                token = User.objects.make_random_password(length=16)
                if not self.__class__.objects.filter(token=token).exists():
                    self.token = token
                    unique = True
        super(APIKey, self).save(*args, **kwargs)

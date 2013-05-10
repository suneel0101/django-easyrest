from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=250)
    text = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    status = models.IntegerField()

    @property
    def popularity(self):
        """
        Some property, which we can expose in the API
        just as easily as any model field
        """
        return self.status + int(self.is_active)


class ProtectedItem(models.Model):
    name = models.CharField(max_length=250)
    text = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    status = models.IntegerField()

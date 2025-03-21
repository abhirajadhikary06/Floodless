from django.db import models

class Calamity(models.Model):
    year = models.IntegerField(null=True, blank=True)
    calamity_type = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.calamity_type} in {self.location}, {self.region}, {self.country} ({self.year})"
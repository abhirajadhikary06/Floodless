from django.db import models

class Disaster(models.Model):
    year = models.IntegerField()
    disaster_type = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.disaster_type} in {self.location} ({self.year})"

    class Meta:
        verbose_name = "Disaster"
        verbose_name_plural = "Disasters"
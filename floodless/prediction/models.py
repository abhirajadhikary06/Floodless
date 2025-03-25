# prediction/models.py
from django.db import models

class DisasterPrediction(models.Model):
    year = models.IntegerField(db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    location = models.CharField(max_length=200)  # Original location string
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    total_affected = models.IntegerField()
    magnitude = models.FloatField()
    disaster_type = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return f"{self.disaster_type} in {self.location}, {self.country} ({self.year})"

class Hospital(models.Model):
    disaster_prediction = models.ForeignKey(DisasterPrediction, on_delete=models.CASCADE, related_name='hospitals')
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.name} near {self.disaster_prediction.location}"
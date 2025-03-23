from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class EmergencyReport(models.Model):
    DISASTER_TYPES = (
        ('flood', 'Flood'),
        ('wildfire', 'Wildfire'),
        ('storm', 'Storm'),
        ('earthquake', 'Earthquake'),
        ('volcanic_eruption', 'Volcanic Eruption'),
        ('drought', 'Drought'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    disaster_type = models.CharField(max_length=50, choices=DISASTER_TYPES)
    description = models.TextField()
    location = models.CharField(max_length=255, null=True, blank=True)  # Manually entered location
    latitude = models.FloatField(null=True, blank=True)  # Live location latitude
    longitude = models.FloatField(null=True, blank=True)  # Live location longitude
    reported_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.disaster_type} reported by {self.user.username} at {self.reported_at}"

class ChatMessage(models.Model):
    report = models.ForeignKey(EmergencyReport, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} in {self.report.disaster_type} at {self.timestamp}"
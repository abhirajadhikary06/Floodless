from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    source = models.CharField(max_length=100)
    is_disaster_related = models.BooleanField(default=False)

    def __str__(self):
        return self.title
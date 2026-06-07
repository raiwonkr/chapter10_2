from django.db import models
from django.contrib.auth.models import User


class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles", null=True)
    title = models.CharField(max_length=500)
    reason = models.TextField()
    summary = models.TextField()
    link = models.URLField(max_length=1000)
    pub_date = models.CharField(max_length=100, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-saved_at"]

    def __str__(self):
        return self.title

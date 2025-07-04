from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Chat(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.message

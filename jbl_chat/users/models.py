from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Delete profile when user is deleted
    image_url = models.CharField(max_length=200, default='https://api.dicebear.com/9.x/avataaars/svg')

    def __str__(self):
        return self.user.username
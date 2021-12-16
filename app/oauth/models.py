from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    avatar_hash = models.CharField(null=True, blank=True, max_length=32)
    access_token = models.CharField(null=True, blank=True, max_length=32)
    refresh_token = models.CharField(null=True, blank=True, max_length=32)
    expires_in = models.DateTimeField(null=True, blank=True)

    discord_roles = models.JSONField(blank=True, default=list)
    guild_member = models.BooleanField(blank=True, default=False)
    guild_officer = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.username

from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)

    is_onboarded = models.BooleanField(default=False)
    is_in_checkin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def display_name(self):
        return self.first_name or self.username or "there"

    def __str__(self):
        return str(self.telegram_id)

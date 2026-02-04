from django.db import models
from datetime import timedelta
from django.utils import timezone

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




class FinancialProfile(models.Model):
    CHECKIN_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("bi-weekly", "Bi-Weekly"),
        ("monthly", "Monthly"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_profile')
    estimated_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    motivation = models.CharField(max_length=255)
    check_in_frequency = models.CharField(max_length=20, choices=CHECKIN_CHOICES, default="weekly")
    last_check_in = models.DateTimeField(null=True, blank=True)

    financial_context = models.JSONField(default=dict, blank=True) # Flexible, AI-friendly context
    behavioral_tag = models.CharField(max_length=200)
    action_plan = models.TextField(help_text="Personalized behavioral plan for the upcoming savings period.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CHECKIN_INTERVALS = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "bi-weekly": timedelta(weeks=2),
        "monthly": timedelta(days=30),
    }

    def get_next_check_in(self):
        """
        Returns the datetime when the next check-in reminder should be sent.
        If user has never checked in, base it on profile creation time.
        """
        base_time = self.last_check_in
        interval = self.CHECKIN_INTERVALS.get(self.check_in_frequency, timedelta(weeks=1))
        return base_time + interval

    def __str__(self):
        return f"{self.user}'s Financial Profile"


class SavingsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_history')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} at {self.recorded_at}"



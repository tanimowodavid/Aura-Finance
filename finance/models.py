from django.db import models
from users.models import User


class FinancialProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='financial_profile'
    )

    estimated_savings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    motivation = models.CharField(max_length=255)
    check_in_frequency = models.CharField(max_length=20, default="weekly")

    # Flexible, AI-friendly context
    financial_context = models.JSONField(
        default=dict,
        blank=True
    )
    action_plan = models.TextField(help_text="Personalized behavioral plan for the upcoming savings period.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s Financial Profile"


class SavingsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_history')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} at {self.recorded_at}"




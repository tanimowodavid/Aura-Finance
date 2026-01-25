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

    savings_goal_note = models.TextField(blank=True)
    last_check_in_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_savings(self, new_amount):
        self.estimated_savings = new_amount
        self.save(update_fields=['estimated_savings', 'updated_at'])

    def __str__(self):
        return f"{self.user}'s Financial Profile"



class CheckIn(models.Model):
    SAVED = 'saved'
    OVERSPENT = 'overspent'
    NO_CHANGE = 'no_change'

    STATUS_CHOICES = [
        (SAVED, 'Saved Money'),
        (OVERSPENT, 'Overspent'),
        (NO_CHANGE, 'No Change'),
    ]

    profile = models.ForeignKey(
        FinancialProfile,
        on_delete=models.CASCADE,
        related_name='checkins'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NO_CHANGE
    )

    savings_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)
    ai_response = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"CheckIn({self.profile.user} - {self.status})"




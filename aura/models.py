from django.db import models
from users.models import User

# Create your models here.

class ChatMessage(models.Model):
    chat_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # "user" | "assistant"
    content = models.TextField()
    session_type = models.CharField(
        max_length=20,
        choices=[
            ("onboarding", "Onboarding"),
            ("check_in", "Check-in"),
            ("general", "General"),
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} @ {self.timestamp}: {self.content[:50]}..."



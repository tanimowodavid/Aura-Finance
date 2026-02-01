from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    path("cron/run-reminders/", views.run_reminders, name="run_reminders"),
]

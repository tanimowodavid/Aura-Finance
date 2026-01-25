# finance/admin.py

from django.contrib import admin
from .models import FinancialProfile, CheckIn


@admin.register(FinancialProfile)
class FinancialProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_savings', 'created_at', 'updated_at']
    search_fields = ['user__telegram_id', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CheckIn)
class SavingsCheckInAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'savings_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__telegram_id', 'user__first_name']
    readonly_fields = ['created_at', 'savings_amount', 'status']
    ordering = ['-created_at']


# aura/tools.py
from users.models import User, FinancialProfile, SavingsHistory
from django.utils import timezone


AURA_ONBOARDING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "finalize_onboarding",
            "description": "Call this ONLY when a NEW user has finished their initial interview to save their profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "estimated_savings": {
                        "type": "number",
                        "description": "The total amount the user has saved."
                    },
                    "motivation": {
                        "type": "string",
                        "description": "The primary reason the user wants to save (e.g., 'buying a house', 'emergency fund')."
                    },
                    "check_in_frequency": {
                        "type": "string",
                        "description": "How often the user wants to be prompted for updates."
                    },
                    "financial_context": {
                        "type": "object",
                        "description": "Dynamic context about income sources, expenses, and habits.",
                        "properties": {
                            "primary_income_source": { "type": "string" }
                        },
                        "additionalProperties": { "type": "string" }
                    },

                    "behavioral_tag": {"type": "string", "description": "e.g., Emotional Spender"},

                    "action_plan": {
                        "type": "string",
                        "description": "Personalized behavioral plan for the upcoming savings period."
                    },
                },
                "required": [
                    "estimated_savings",
                    "motivation",
                    "check_in_frequency",
                    "financial_context",
                    "behavioral_tag",
                    "action_plan",
                ]
            }
        }
    }
]

AURA_CHECKIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "finish_check_in",
            "description": "Finalizes the session, updates the total savings, and refreshes the action plan.",
            "parameters": {
            "type": "object",
            "properties": {
                "latest_savings": {
                "type": "number",
                "description": "The user's newly reported total savings balance."
                },
                "action_plan": {
                "type": "string",
                "description": "A 3-step behavioral plan based on the current check-in conversation."
                },
                "context_update": {
                "type": "object",
                "description": "Any new income or expense details learned during this chat.",
                "additionalProperties": { "type": "string" }
                }
            },
            "required": ["latest_savings", "action_plan"]
            }
        }
    }
]


def finalize_onboarding(user_id: int, estimated_savings, motivation, check_in_frequency, financial_context, behavioral_tag, action_plan):
    """
    Called by Aura (GPT function calling).
    Creates or updates the user's financial profile and marks onboarding as complete.
    """

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"status": "error", "message": "User not found."}

    profile, created = FinancialProfile.objects.get_or_create(user=user)

    profile.estimated_savings = estimated_savings
    profile.motivation = motivation
    profile.check_in_frequency = check_in_frequency
    profile.financial_context = financial_context
    profile.behavioral_tag = behavioral_tag
    profile.action_plan = action_plan
    profile.save()

    SavingsHistory.objects.get_or_create(user=user, amount=estimated_savings)

    user.is_onboarded = True
    user.save(update_fields=["is_onboarded"])

    return {
        "status": "success",
        "onboarded": True,
        "user_id": user.id,
        "estimated_savings": str(estimated_savings),
        "motivation": motivation,
        "check_in_frequency": check_in_frequency,
        "financial_context": financial_context,
        "behavioral_tag": behavioral_tag,
        "action_plan": action_plan,
    }



def finish_check_in(user_id, latest_savings, action_plan, context_update=None):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"status": "error", "message": "User not found."}

    profile = user.financial_profile
    context_update = context_update or {}

    # 1. Calculate Velocity (The PAW Metric)
    # Get the last recorded entry before this update
    previous_entry = user.savings_history.order_by('-recorded_at').first()
    previous_amount = float(previous_entry.amount) if previous_entry else 0
    velocity = float(latest_savings) - previous_amount

    # 2. Update Profile
    profile.estimated_savings = latest_savings
    profile.action_plan = action_plan
    profile.financial_context = {**profile.financial_context, **context_update}
    profile.save()

    # 3. Save History
    SavingsHistory.objects.create(user=user, amount=latest_savings)

    # 4. Release Check-in State
    user.is_in_checkin = False
    user.save(update_fields=["is_in_checkin"])

    return {
        "status": "success",
        "velocity": velocity,
        "is_up": velocity > 0,
        "latest_savings": float(latest_savings),
        "action_plan": action_plan,
        "behavioral_tag": profile.behavioral_tag
    }

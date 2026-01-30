# aura/tools.py
from finance.models import FinancialProfile, SavingsHistory
from users.models import User
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
                    "description": "Additional financial context about the user (income sources, expenses, challenges, etc.)",
                    "properties": {}
                },
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
            "description": "Mark a check-in as complete and update the user's savings + financial context.",
            "parameters": {
                "type": "object",
                "properties": {
                "latest_savings": {
                    "type": "number",
                    "description": "The user's newly reported savings total."
                },
                "context_update": {
                    "type": "object",
                    "description": "A partial update to merge into financial_context.",
                    "additionalProperties": True
                },
                "action_plan": {
                    "type": "string",
                    "description": "Personalized behavioral plan for the upcoming savings period."
                }
                },
                "required": ["latest_savings", "action_plan"]
            }
        }
    }
]



def finalize_onboarding(user_id: int, estimated_savings, motivation, check_in_frequency, financial_context, action_plan):
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
    profile.action_plan = action_plan
    profile.save()

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
        "action_plan": action_plan,
    }


def finish_check_in(user_id, args):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"status": "error", "message": "User not found."}
    
    user.is_in_checkin = False
    user.save()

    profile = user.financial_profile

    latest = args["latest_savings"]
    context_update = args.get("context_update", {})
    action_plan = args["action_plan"]

    # Update main savings value
    profile.estimated_savings = latest
    profile.action_plan = action_plan

    # Merge contexts
    profile.financial_context = {
        **profile.financial_context,
        **context_update
    }
    profile.save()

    # Save savings history
    SavingsHistory.objects.create(
        user=user,
        amount=latest
    )


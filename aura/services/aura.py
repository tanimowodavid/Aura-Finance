from users.models import User
from finance.models import FinancialProfile, CheckIn
from .gemini import generate_response
from aura.prompts import AURA_SYSTEM_PROMPT
from decimal import Decimal


def handle_message(telegram_id: int, text: str) -> str:
    user, _ = User.objects.get_or_create(
        telegram_id=telegram_id
    )

    text = text.strip().lower()

    if text.startswith("/start"):
        return start_flow(user)

    if not user.is_onboarded:
        return onboarding_flow(user, text)

    if text.startswith("/checkin"):
        return checkin_flow(user)

    if text.startswith("/stats"):
        return stats_flow(user)

    if text.startswith("/motivate"):
        return motivate_flow(user)

    if text.startswith("/advise"):
        return advise_flow(user)

    return free_chat_flow(user, text)


# ---------- FLOWS ----------

def start_flow(user: User) -> str:
    if user.is_onboarded:
        return (
            "Welcome back 👋\n\n"
            "You can:\n"
            "/checkin – reflect on savings\n"
            "/stats – see your progress\n"
            "/motivate – get encouragement\n"
            "/advise – practical saving advice"
        )

    return (
        "Hi, I’m *Aura* 💰\n\n"
        "I help you save more money through reflection and mindset.\n\n"
        "Let’s begin.\n"
        "How much do you currently have saved? (number only)"
    )


def onboarding_flow(user: User, text: str) -> str:
    profile = getattr(user, "financial_profile", None)

    if not profile:
        try:
            amount = Decimal(text)
        except:
            return "Please enter a valid number for your savings."

        FinancialProfile.objects.create(
            user=user,
            estimated_savings=amount
        )
        return "Got it. What are you saving for? (short note)"

    if not profile.savings_goal_note:
        profile.savings_goal_note = text
        profile.save()

        user.is_onboarded = True
        user.save()

        return (
            "You’re all set 🎉\n\n"
            "Remember: paying yourself first builds freedom.\n\n"
            "Come back anytime and type /checkin."
        )

    return "Onboarding already completed."


def checkin_flow(user: User) -> str:
    return (
        "Let’s check in 💡\n\n"
        "Have your savings increased since the last time?\n"
        "Reply with the new total amount."
    )


def process_checkin_amount(user: User, text: str) -> str:
    try:
        new_amount = Decimal(text)
    except:
        return "Please enter a valid number."

    profile = user.financial_profile
    delta = new_amount - profile.estimated_savings

    profile.estimated_savings = new_amount
    profile.last_check_in_at = profile.updated_at
    profile.save()

    status = "no_change"
    if delta > 0:
        status = "saved"
    elif delta < 0:
        status = "overspent"

    CheckIn.objects.create(
        user=user,
        status=status,
        notes=f"Delta: {delta}"
    )

    if delta > 0:
        return f"Great job 🎉 You saved {delta}. Small wins matter."
    elif delta < 0:
        return "That’s okay. Awareness comes before discipline."
    else:
        return "No change. Staying steady is still progress."


def stats_flow(user: User) -> str:
    profile = user.financial_profile
    return (
        f"*Your Savings Snapshot*\n\n"
        f"Total saved: {profile.estimated_savings}\n"
        f"Goal: {profile.savings_goal_note or '—'}"
    )


def motivate_flow(user: User) -> str:
    return generate_response(
        AURA_SYSTEM_PROMPT,
        "Give a short motivational message about saving money."
    )


def advise_flow(user: User) -> str:
    return generate_response(
        AURA_SYSTEM_PROMPT,
        "Give one practical saving advice inspired by finance books."
    )


def free_chat_flow(user: User, text: str) -> str:
    return generate_response(
        AURA_SYSTEM_PROMPT,
        text
    )

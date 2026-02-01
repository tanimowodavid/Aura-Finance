import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aura.services.aura import handle_onboarding_message, handle_general_message, handle_checkin_message
from aura.utils import send_message
from users.models import User, FinancialProfile
from django.utils import timezone
from aura.services.llm import send_checkin_reminder


@csrf_exempt
def telegram_webhook(request):
    data = json.loads(request.body.decode("utf-8"))
    if "message" not in data:
        return JsonResponse({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]
    telegram_id = message["from"]["id"]
    text = message.get("text", "")

    # 1. Fetch user once. Using get_or_create ensures 'user' always exists.
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"first_name": message["from"].get("first_name", "")}
    )

    # 2. Routing Logic (using the 'user' object in memory)
    if not user.is_onboarded:
        response = handle_onboarding_message(user, message)
    
    elif user.is_in_checkin or text in ["/start", "/checkin"]:
        # If they aren't marked as 'in_checkin' yet but sent the command, update them
        if not user.is_in_checkin:
            user.is_in_checkin = True
            user.save()
        response = handle_checkin_message(user, message)
    
    else:
        response = handle_general_message(user, message)

    # 3. Final Action
    send_message(chat_id, response)
    return JsonResponse({"ok": True})




# send checkin reminder to the users
def run_reminders(request):
    now = timezone.now()
    triggered = []

    profiles = FinancialProfile.objects.all()

    for profile in profiles:
        next_time = profile.get_next_check_in()

        if now >= next_time:
            reminder = send_checkin_reminder(profile)
            send_message(profile.user.telegram_id, reminder)
            profile.last_check_in = now
            profile.save()
            triggered.append(profile.user.first_name)

    return JsonResponse({
        "status": "ok",
        "triggered_for": triggered
    })


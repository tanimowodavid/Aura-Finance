import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aura.services.aura import handle_message
from aura.utils import send_message


@csrf_exempt
def telegram_webhook(request):
    data = json.loads(request.body.decode("utf-8"))

    if "message" not in data:
        return JsonResponse({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]
    telegram_id = message["from"]["id"]
    text = message.get("text", "")

    response = handle_message(telegram_id, text)

    send_message(chat_id, response)

    return JsonResponse({"ok": True})

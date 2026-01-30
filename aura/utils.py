import requests
from django.conf import settings

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

def send_message(chat_id: int, text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=5)


def format_history(chat_id, session_type):
    from aura.models import ChatMessage

    messages = ChatMessage.objects.filter(chat_id=chat_id, session_type=session_type).order_by("timestamp")

    formatted = []
    for msg in messages:
        formatted.append({
            "role": msg.role,
            "content": msg.content
        })

    return formatted

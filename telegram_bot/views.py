import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from asgiref.sync import sync_to_async
from telegram_bot.bot import setup_bot

# Initialize bot once
application = setup_bot()

@csrf_exempt
async def telegram_webhook(request):
    """Handle incoming webhook requests from Telegram."""
    if request.method == 'POST':
        try:
            body = await sync_to_async(request.body.decode)('utf-8')
            update = Update.de_json(json.loads(body), application.bot)
            await application.process_update(update)
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from .bot import application # Import the engine from bot.py

@csrf_exempt
async def telegram_webhook(request):
    """Handle incoming Telegram updates."""
    if request.method == "POST":
        try:
            # 1. Ensure the bot application is initialized and started
            if not application.running:
                await application.initialize()
                await application.start()

            # 2. Convert the raw request body into a Telegram Update object
            data = json.loads(request.body.decode("utf-8"))
            update = Update.de_json(data, application.bot)

            # 3. Process the update through our handlers (start command, etc.)
            await application.process_update(update)
            
            return HttpResponse("OK", status=200)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return HttpResponse("Internal Error", status=500)

    return HttpResponse("Invalid Method", status=405)
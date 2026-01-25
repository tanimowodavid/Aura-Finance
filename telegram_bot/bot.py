import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Simple 'Hi' Logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a static greeting when /start is issued."""
    await update.message.reply_text("👋 Hello! Welcome to our bot. How can I help you today?")

# 2. Singleton Initialization
# This creates the application object ONCE when the server starts
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# We use 'updater=None' because we are using Webhooks, not Polling
application = Application.builder().token(TOKEN).updater(None).build()

# Add handlers
application.add_handler(CommandHandler("start", start))

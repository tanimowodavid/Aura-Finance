import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a greeting when /start is issued."""
    user = update.effective_user
    greeting = f"👋 Hello {user.first_name}! Welcome to our bot. How can I help you today?"
    await update.message.reply_text(greeting)

def setup_bot():
    """Initialize and configure the bot."""
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    return application
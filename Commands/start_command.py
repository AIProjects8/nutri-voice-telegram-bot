from telegram import Update
from telegram.ext import ContextTypes
from config import Config

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm {Config.from_env().bot_username}")
    
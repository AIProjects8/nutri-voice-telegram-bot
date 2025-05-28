from telegram import Update
from telegram.ext import ContextTypes
from Tools.auth_helper import restricted
from Tools.openai_manager import OpenAIManager
from SqlDB.middleware import update_db_user
from SqlDB.user_cache import UserCache

@restricted
@update_db_user
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    telegram_user_id: int = update.message.from_user.id
    
    print(f"User ({telegram_user_id}) in {message_type}: {text}")
    
    if message_type == "group":
        await update.message.reply_text("Group chats are not supported yet.")
        return

    openai_manager = OpenAIManager()
    response_text = await openai_manager.process_text(telegram_user_id, text)
    await update.message.reply_text(response_text)
from telegram import Update
from telegram.ext import ContextTypes
import os
from Tools.auth_helper import restricted
from Tools.openai_manager import OpenAIManager
from SqlDB.middleware import update_db_user

@restricted
@update_db_user
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    text = update.message.caption or "Describe what you see on the image."
    file = await context.bot.get_file(photo.file_id)
    
    image_path = f'./images/image_{photo.file_unique_id}.jpg'
    os.makedirs('./images', exist_ok=True)
    await file.download_to_drive(image_path)
    
    openai_manager = OpenAIManager()
    response_text = await openai_manager.process_image(update.message.from_user.id, image_path, text)
    
    await update.message.reply_text(response_text)
    
    os.remove(image_path)
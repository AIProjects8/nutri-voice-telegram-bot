from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

import os
load_dotenv()

token = os.getenv("TELEGRAM_BOT_API_KEY")
bot_username = os.getenv("BOT_USERNAME")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}, I'm {bot_username}")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Start the bot")
    await update.message.reply_text("/help - Get help")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command, you can add any message here.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    
def handle_response(text: str) -> str:
    processed: str = text.lower()
    
    if "hello" in processed:
        return "Hey there!"
    
    return "I don't understand"
  
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f"User ({update.message.chat.id}) in {message_type}: {text}")
    
    if message_type == "group":
        if bot_username in text:
            new_text: str = text.replace(bot_username, "").strip()
            response: str = handle_response(new_text)
            
            await update.message.reply_text(response)
        else:
          return        
    else:
      response: str = handle_response(text)
    
    print(f"Bot response: {response}")
    await update.message.reply_text(response)
    
if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    app.add_error_handler(error)
    
    print("Bot is running...")
    app.run_polling(poll_interval=3)
            
    
    





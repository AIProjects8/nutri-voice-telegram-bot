from telegram import Update
from telegram.ext import ContextTypes
from auth_helper import restricted
from openai_tools import OpenAIClient
from config import Config

@restricted
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f"User ({update.message.chat.id}) in {message_type}: {text}")
    
    if message_type == "group":
        await update.message.reply_text("Group chats are not supported yet.")
        return

    response = OpenAIClient.get_instance().client.chat.completions.create(
        model=Config.from_env().gpt_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Always respond in Polish language."},
            {"role": "user", "content": text}
        ]
    )
    
    response_text = response.choices[0].message.content
    await update.message.reply_text(response_text)
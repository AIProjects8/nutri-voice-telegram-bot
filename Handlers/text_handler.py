from telegram import Update
from telegram.ext import ContextTypes
from auth_helper import restricted
from openai_tools import OpenAIClient
from config import Config
from conversation_manager import ConversationManager

@restricted
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user_id: int = update.message.from_user.id
    
    print(f"User ({user_id}) in {message_type}: {text}")
    
    if message_type == "group":
        await update.message.reply_text("Group chats are not supported yet.")
        return

    conv_manager = ConversationManager()
    conv_manager.add_message(user_id, "user", text)
    messages = conv_manager.get_conversation_history(user_id)

    response = OpenAIClient.get_instance().client.chat.completions.create(
        model=Config.from_env().gpt_model,
        messages=messages
    )
    
    response_text = response.choices[0].message.content
    conv_manager.add_message(user_id, "assistant", response_text)
    
    await update.message.reply_text(response_text)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from Commands.help_command import help_command
from Commands.start_command import start_command
from config import Config
from Handlers.image_handler import handle_image
from Handlers.text_handler import handle_text
from Handlers.voice_handler import handle_voice
from SqlDB import initialize_database
from Tools.errors_handler import error

# Initialize configuration
config = Config.from_env()
config.validate()

if __name__ == "__main__":
    print("Starting bot...")

    # Initialize database
    print("Initializing database...")
    initialize_database()

    app = Application.builder().token(config.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    app.add_error_handler(error)

    print("Bot is running...")
    app.run_polling(poll_interval=3)

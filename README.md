# NutriVoice Telegram Bot

A Telegram bot that helps users with nutrition-related queries through voice messages.

## Prerequisites

- Python 3.12
- Telegram Bot Token (obtained from BotFather)
- OpenAI API Key

## Bot Setup with BotFather

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat with BotFather and follow these commands:
   - `/newbot` - Create a new bot
     - Choose a name for your bot
     - Choose a username (must end with 'bot')
     - Save the API token provided
   - `/setdescription` - Set a description for your bot
   - `/setcommands` - Set the following command:
     ```
     start - Start the bot and register your user ID
     ```
   - `/setjoingroups` - Disable group functionality (this bot is for private conversations only)

## Project Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd nutri-voice-telegram-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your credentials:
   ```
  TELEGRAM_BOT_API_KEY= (get from BotFather)
  BOT_USERNAME=@bot_name (get from BotFather;)
  OPENAI_API_KEY= (get from OpenAI)
  VOICE_RESPONSE=false (true if you want to have voice responses when sending voice requests)
  GPT_MODEL="gpt-4o-mini" (choose whatever model you want but it needs to be able to process images and have function calling)
  ALLOWED_USER_IDS= (your user id, you can get it when calling /start command)
  POSTGRES_USER=postgres (db user)
  POSTGRES_PASSWORD=postgres (db password)
  POSTGRES_DB=nutri_voice (db name)
   ```

   Note: To get your USER_ID:
   1. Start the bot using the `/start` command
   2. The bot will display your user ID
   3. Add this ID to the .env file

5. Set up database:
  ```bash
  docker compose up
  ```

  If you have problems with setting up database, remove it together with volume:
  ```bash
  docker compose down -v
  ```

## Running the Bot

1. Make sure your virtual environment is activated
2. Run the bot:
   ```bash
   python main.py
   ```

## Features

- Voice message processing
- Nutrition-related queries
- Private conversation mode
- User-specific interactions

## Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- The bot is designed for private conversations only

## License

This project is licensed under the MIT License - see the LICENSE file for details.

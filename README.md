# NutriVoice Telegram Bot

A Telegram bot that can process voice messages, images, and provide responses using OpenAI's GPT-4 Vision and Whisper APIs.

![image](https://github.com/user-attachments/assets/48cf2ad6-da1b-42d7-bbba-8fe4c2eabe27)

## Features

- 🎤 Voice message processing with OpenAI Whisper
- 🖼️ Image analysis with GPT-4 Vision
- 🔊 Text-to-speech responses
- 🇵🇱 Polish language support

## Prerequisites

- Python 3.7.1 or newer
- OpenAI API key
- Telegram Bot Token (from BotFather)

## Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd nutri-voice-telegram-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```env
TELEGRAM_BOT_API_KEY="your-telegram-bot-token"
BOT_USERNAME="@your-bot-username"
OPENAI_API_KEY="your-openai-api-key"
```

## BotFather Setup

1. Open Telegram and search for @BotFather
2. Start a chat and use the `/newbot` command
3. Follow the instructions to:
   - Choose a name for your bot
   - Choose a username (must end in 'bot')
4. BotFather will provide you with a token
5. Copy the token and add it to your `.env` file

## Running the Bot

1. Make sure your virtual environment is activated
2. Run the bot:
```bash
python main.py
```

## Usage

- Send voice messages to get transcribed and analyzed responses
- Send images to get descriptions in Polish
- The bot will respond with both text and voice messages

## Directory Structure

```
nutri-voice-telegram-bot/
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── audio/              # Temporary audio files
└── images/             # Temporary image files
```

## Dependencies

- python-telegram-bot
- openai
- python-dotenv
- requests

## Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- The bot temporarily stores audio and image files, which are automatically deleted after processing

## License

MIT

import os

from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from SqlDB.middleware import update_db_user
from Tools.auth_helper import restricted
from Tools.openai_manager import OpenAIManager
from Tools.speech_manager import SpeechManager


@restricted
@update_db_user
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    audio_path = f"./audio/voice_{update.message.voice.file_unique_id}.ogg"

    speech_manager = SpeechManager()
    await speech_manager.download_voice_file(audio_file.file_path, audio_path)
    transcribed_text = await speech_manager.transcribe_voice(audio_path)

    openai_manager = OpenAIManager()
    response_text = await openai_manager.process_text(
        update.message.from_user.id, transcribed_text
    )

    os.remove(audio_path)

    if Config.from_env().voice_response:
        await update.message.reply_text(response_text)
        return

    response_audio_path = f"./audio/response_{update.message.message_id}.mp3"
    await speech_manager.text_to_speech(response_text, response_audio_path)

    await update.message.reply_voice(voice=open(response_audio_path, "rb"))
    os.remove(response_audio_path)

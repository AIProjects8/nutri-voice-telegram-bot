from telegram import Update
from telegram.ext import ContextTypes
import os
import requests
from openai_tools import OpenAIClient
from config import Config
from auth_helper import restricted

@restricted
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    audio_path = f'./audio/voice_{update.message.voice.file_unique_id}.ogg'

    os.makedirs('./audio', exist_ok=True)
    
    with open(audio_path, 'wb') as f:
        response = requests.get(audio_file.file_path)
        f.write(response.content)

    with open(audio_path, "rb") as file:
        transcription = OpenAIClient.get_instance().client.audio.transcriptions.create(
            model="whisper-1", 
            file=file
        )
    transcribed_text = transcription.text

    await process_and_reply(update, context, transcribed_text)
    
async def process_and_reply(update, context, input_text):
    print(f"Processing input: {input_text}")
    
    response = OpenAIClient.get_instance().client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": input_text}
        ]
    )
    response_text = response.choices[0].message.content
    

    if Config.from_env().voice_response:
        await update.message.reply_text(response_text)
        return
    
    speech_response = OpenAIClient.get_instance().client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response_text
    )
    
    audio_path = f'./audio/response_{update.message.message_id}.mp3'
    with open(audio_path, 'wb') as f:
        f.write(speech_response.content)
    
    await update.message.reply_voice(voice=open(audio_path, 'rb'))
    os.remove(audio_path)
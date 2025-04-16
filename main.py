from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
import requests
import os
import base64

load_dotenv()

token = os.getenv("TELEGRAM_BOT_API_KEY")
bot_username = os.getenv("BOT_USERNAME")
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key=openai_api_key)

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
    
async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Download and save the audio file
    audio_file = await context.bot.get_file(update.message.voice.file_id)
    audio_path = f'./audio/voice_{update.message.voice.file_unique_id}.ogg'
    
    # Create the audio directory if it doesn't exist
    os.makedirs('./audio', exist_ok=True)
    
    with open(audio_path, 'wb') as f:
        response = requests.get(audio_file.file_path)
        f.write(response.content)

    # Transcribe the audio file with Whisper API
    with open(audio_path, "rb") as file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=file
        )
    transcribed_text = transcription.text

    await process_and_reply(update, context, transcribed_text)
    
async def process_and_reply(update, context, input_text):
    print(f"Processing input: {input_text}")
    
    # Generate response using OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": input_text}
        ]
    )
    response_text = response.choices[0].message.content
    
    # Convert response to speech
    speech_response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response_text
    )
    
    # Save the audio file
    audio_path = f'./audio/response_{update.message.message_id}.mp3'
    with open(audio_path, 'wb') as f:
        f.write(speech_response.content)
    
    # Send both text and voice response
    # await update.message.reply_text(response_text)
    await update.message.reply_voice(voice=open(audio_path, 'rb'))
    
    # Clean up the audio file
    os.remove(audio_path)
    
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # Download the image
    image_path = f'./images/image_{photo.file_unique_id}.jpg'
    os.makedirs('./images', exist_ok=True)
    
    await file.download_to_drive(image_path)
    
    # Process the image with OpenAI
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        response = openai_client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "user", "content": "What's in this image?"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ]
        )
    
    # Send the description
    description = response.output_text
    await update.message.reply_text(description)
    
    # Clean up
    os.remove(image_path)

if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_audio_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    app.add_error_handler(error)
    
    print("Bot is running...")
    app.run_polling(poll_interval=3)
            
    
    





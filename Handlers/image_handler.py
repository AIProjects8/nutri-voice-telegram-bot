from telegram import Update
from telegram.ext import ContextTypes
import os
import base64
from openai_tools import OpenAIClient
from auth_helper import restricted

@restricted
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    text = update.message.caption or "Describe what you see on the image."
    file = await context.bot.get_file(photo.file_id)
    
    # Download the image
    image_path = f'./images/image_{photo.file_unique_id}.jpg'
    os.makedirs('./images', exist_ok=True)
    
    await file.download_to_drive(image_path)
    
    # Process the image with OpenAI
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        response = OpenAIClient.get_instance().client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": "You are a helpful assistant. Always respond in Polish language."},
                {"role": "user", "content": text},
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
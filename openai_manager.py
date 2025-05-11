from typing import Optional, List, Dict, Any
import base64
from openai_tools import OpenAIClient
from config import Config
from conversation_manager import ConversationManager
from image_helper import encode_image_to_data_url

class OpenAIManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIManager, cls).__new__(cls)
        return cls._instance

    async def process_text(self, user_id: int, text: str) -> str:
        conv_manager = ConversationManager()
        conv_manager.add_message(user_id, "user", text)
        messages = conv_manager.get_conversation_history(user_id)
        
        response = OpenAIClient.get_instance().client.responses.create(
            model=Config.from_env().gpt_model,
            input=messages,
            instructions="You are a helpful assistant. Always respond in Polish language."
        )
        
        response_text = response.output_text
        conv_manager.add_message(user_id, "assistant", response_text)
        
        return response_text

    async def process_image(self, user_id: int, image_path: str, text: str) -> str:
        conv_manager = ConversationManager()
        
        data_url = encode_image_to_data_url(image_path)
        
        input_content = [
            {
                "type": "input_text",
                "text": text
            },
            {
                "type": "input_image",
                "image_url": data_url
            }
        ]
        
        conv_manager.add_message(user_id, "user", input_content)
        messages = conv_manager.get_conversation_history(user_id)
        
        response = OpenAIClient.get_instance().client.responses.create(
            model=Config.from_env().gpt_model,
            input=messages,
            instructions="You are a helpful assistant. Always respond in Polish language."
        )
        
        response_text = response.output_text
        conv_manager.add_message(user_id, "assistant", response_text)
        
        return response_text 
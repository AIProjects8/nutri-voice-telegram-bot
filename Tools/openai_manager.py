
from Tools.openai_tools import OpenAIClient
from config import Config
from Tools.conversation_manager import ConversationManager
from Tools.image_helper import encode_image_to_data_url
from Constants.prompts import PromptsConstants
from SqlDB.user_details_service import get_user_details
from SqlDB.user_cache import UserCache
from Tools.survey_agent import SurveyManager


class OpenAIManager:
    _instance = None
    _survey_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIManager, cls).__new__(cls)
        return cls._instance

    @property
    def survey_manager(self):
        if self._survey_manager is None:
            self._survey_manager = SurveyManager()
        return self._survey_manager

    async def process_text(self, telegram_user_id: int, text: str) -> str:
        conv_manager = ConversationManager()
        db_user_id = UserCache().get_user_id(telegram_user_id)

        if not get_user_details(db_user_id):
            return self.survey_manager.process_survey_message(db_user_id, text)

        conv_manager.add_message(db_user_id, "user", text)
        messages = conv_manager.get_conversation_history(db_user_id)

        response = OpenAIClient.get_instance().client.responses.create(
            model=Config.from_env().gpt_model,
            input=messages,
            instructions=PromptsConstants.CHAT_MAIN_PROMPT
        )

        response_text = response.output_text
        conv_manager.add_message(db_user_id, "assistant", response_text)

        return response_text

    async def process_image(self, telegram_user_id: int, image_path: str, text: str) -> str:
        conv_manager = ConversationManager()
        db_user_id = UserCache().get_user_id(telegram_user_id)

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

        conv_manager.add_message(db_user_id, "user", input_content)
        messages = conv_manager.get_conversation_history(db_user_id)

        response = OpenAIClient.get_instance().client.responses.create(
            model=Config.from_env().gpt_model,
            input=messages,
            instructions=PromptsConstants.CHAT_MAIN_PROMPT
        )

        response_text = response.output_text
        conv_manager.add_message(db_user_id, "assistant", response_text)

        return response_text

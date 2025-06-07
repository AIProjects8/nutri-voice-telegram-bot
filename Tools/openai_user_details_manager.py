from datetime import datetime
from Constants.settings import SettingsConstants
from Constants.tools import ToolDescriptionConstants
from Constants.prompts import PromptsConstants, SystemPromptsConstants
from Tools.openai_tools import OpenAITools
from SqlDB.user_details_service import create_user_details
from config import Config
from Tools.openai_session import OpenAIRequestConfig, GeneralOpenAIHandler


class OpenAIUserDetailsManager:
    def __init__(self):
        self.handler = GeneralOpenAIHandler()

    def _get_user_details_from_answers(self, answers: dict, user_id: str) -> dict:
        """Extract user details from survey answers using OpenAI."""
        answers_text = "\n".join(f"{q}: {a}" for q, a in answers.items())
        user_prompt = PromptsConstants.SURVEY_ANSWERS_PROMPT.format(
            answers_text=answers_text, user_id=user_id
        )
        system_prompt = SystemPromptsConstants.SURVEY_ANSWERS_ASSISTANT

        result = self.handler.make_json_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=Config.from_env().gpt_model,
            temperature=0.0
        )

        if result["success"]:
            return result["parsed_json"]
        else:
            raise Exception(f"Failed to get user details: {result['error']}")

    def ask_question(self, question: str, user_input: str) -> str:
        """Validate user answer using GPT with function calling."""
        max_date = datetime.now().year
        min_date = max_date - 100

        system_prompt = SystemPromptsConstants.MEDICAL_INTAKE_ASSISTANT.format(
            min_date=min_date,
            max_date=max_date,
            no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT
        )
        user_prompt = PromptsConstants.SURVEY_QUESTION_PROMPT.format(
            question=question, user_input=user_input
        )

        messages = [
            self.handler.create_message("system", system_prompt),
            self.handler.create_message("user", user_prompt)
        ]

        config = OpenAIRequestConfig(
            model=Config.from_env().gpt_model,
            temperature=0.5,
            tools=[ToolDescriptionConstants.VALIDATE_RANGE],
            max_retries=SettingsConstants.MAX_SURVEY_REQUESTS
        )

        result = self.handler.make_request(
            messages, config, OpenAITools.handle_call_function)

        if result["success"] and result["response_text"]:
            return result["response_text"]
        else:
            return PromptsConstants.SURVEY_PROMPT_ERROR

    def create_user_details_from_answers(self, answers: dict, user_id: str) -> bool:
        """Create UserDetails object from survey answers and save to database."""
        try:
            details = self._get_user_details_from_answers(answers, user_id)

            create_user_details(
                user_id=details["user_id"],
                weight=float(details["weight"]),
                year_of_birth=int(details["year_of_birth"]),
                gender=details["gender"],
                allergies=details["allergies"]
            )
            return True

        except Exception as e:
            print(f"Error creating user details: {str(e)}")
            return False

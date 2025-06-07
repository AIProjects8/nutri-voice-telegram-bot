from datetime import datetime
from Constants.settings import SettingsConstants
from Constants.tools import ToolDescriptionConstants
from Constants.prompts import PromptsConstants, SystemPromptsConstants
from SqlDB.user_details_service import create_user_details
from config import Config
from Tools.openai_session import OpenAIRequestConfig, GeneralOpenAIHandler
from typing import Dict, Any
import json
from Tools.openai_tools import OpenAITools


class OpenAIUserDetailsManager:
    def __init__(self):
        self.handler = GeneralOpenAIHandler()

    def _get_user_details_from_answers(self, answers: str) -> dict:
        """Extract user details from survey answers using OpenAI."""
        # answers_text = "\n".join(f"{q}: {a}" for q, a in answers.items())
        user_prompt = PromptsConstants.SURVEY_ANSWERS_PROMPT.format(
            answers_text=answers
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
            no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT,
            parse_error_response=PromptsConstants.SURVEY_PARSE_ERROR
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
            details = self._get_user_details_from_answers(answers)

            create_user_details(
                user_id=user_id,
                weight=float(details["weight"]),
                year_of_birth=int(details["year_of_birth"]),
                gender=details["gender"],
                allergies=details["allergies"]
            )
            return True

        except Exception as e:
            print(f"Error creating user details: {str(e)}")
            return False

    def confirm_user_details(self, current_user_data: dict, user_response: str) -> Dict[str, Any]:
        """
            Process user confirmation response and return changes they want to make.

            Args:
                current_user_data: Current user data dict with keys: weight, year_of_birth, gender, allergies
                user_response: User's response to confirmation question

            Returns:
                Dict with keys:
                - success: bool indicating if processing was successful
                - changes: dict with only the fields user wants to change (empty if confirming all)
                - error: error message if any
                - action: "confirm_all", "update", or "unclear"
            """
        try:
            # Format current data for display
            # current_data_text = self._format_current_data_for_display(
            #     current_user_data)

            # Prepare prompts
            max_date = datetime.now().year
            min_date = max_date - 100

            system_prompt = SystemPromptsConstants.CONFIRMATION_SYSTEM_ASSISTANT.format(
                min_date=min_date,
                max_date=max_date,
                parse_error_response=PromptsConstants.SURVEY_PARSE_ERROR,
                no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT,
            )

            user_prompt = PromptsConstants.CONFIRMATION_USER_PROMPT.format(
                current_data=current_user_data,
                user_response=user_response
            )

            # Prepare messages and config
            messages = [
                self.handler.create_message("system", system_prompt),
                self.handler.create_message("user", user_prompt)
            ]

            config = OpenAIRequestConfig(
                model=Config.from_env().gpt_model,
                temperature=0.3,
                tools=[
                    ToolDescriptionConstants.VALIDATE_RANGE,
                ],
                max_retries=4
            )

            # Make the request
            result = self.handler.make_request(
                messages, config, OpenAITools.handle_call_function)

            if not result["success"]:
                return {
                    "success": False,
                    "changes": {},
                    "error": result["error"],
                    "action": "error"
                }

            response_text = result["response_text"].strip()

            # Handle special responses
            if response_text == PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT:
                return {
                    "success": True,
                    "changes": {},
                    "error": "Nie rozumiem odpowiedzi. Czy możesz sprecyzować?",
                    "action": "unclear"
                }

            if response_text == PromptsConstants.SURVEY_PARSE_ERROR:
                return {
                    "success": True,
                    "changes": {},
                    "error": "Wystąpił błąd podczas przetwarzania danych.",
                    "action": "error"
                }

            try:

                # Empty JSON means user confirms everything
                if not response_text:
                    return {
                        "success": True,
                        "changes": {},
                        "error": None,
                        "action": "not_confirm_all"
                    }
                if response_text == "tak":
                    return {
                        "success": True,
                        "changes": {},
                        "error": None,
                        "action": "confirm_all"
                    }
                current_user_data_str = json.dumps(current_user_data)
                combined_text = response_text + current_user_data_str
                details = self._get_user_details_from_answers(
                    combined_text)
                return {
                    "success": True,
                    "changes": details,
                    "error": None,
                    "action": "update"
                }

            except json.JSONDecodeError:
                return {
                    "success": False,
                    "changes": {},
                    "error": "Nie udało się przetworzyć odpowiedzi.",
                    "action": "error"
                }
        except Exception as e:
            return {
                "success": False,
                "changes": {},
                "error": str(e),
                "action": "error"
            }

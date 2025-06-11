import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from config import Config
from Constants.const import Constants
from Constants.prompts import PromptsConstants, SystemPromptsConstants
from Constants.responses import ResponsesConstants
from Constants.tools import ToolDescriptionConstants
from SqlDB.user_details_service import create_user_details
from Tools.openai_session import GeneralOpenAIHandler, OpenAIRequestConfig
from Tools.openai_tools import OpenAITools


@dataclass
class UserDetailsResponse:
    """Response class for user details operations."""

    success: bool
    changes: Dict[str, Any]
    error: Optional[str]
    action: str

    @classmethod
    def success_response(
        cls, changes: Dict[str, Any] = None, action: str = Constants.ACTION_CONFIRM_ALL
    ) -> "UserDetailsResponse":
        """Create a successful response."""
        return cls(success=True, changes=changes or {}, error=None, action=action)

    @classmethod
    def error_response(
        cls, error: str, action: str = Constants.ERROR
    ) -> "UserDetailsResponse":
        """Create an error response."""
        return cls(success=False, changes={}, error=error, action=action)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            Constants.SUCCESS: self.success,
            Constants.CHANGES: self.changes,
            Constants.ERROR: self.error,
            Constants.ACTION: self.action,
        }


class OpenAIDetailsRequestHandler:
    """Handles OpenAI requests for user details operations."""

    def __init__(self):
        self.handler = GeneralOpenAIHandler()
        self.model = Config.from_env().gpt_model

    def _create_request_config(
        self, temperature: float = 0.0, tools: list = None
    ) -> OpenAIRequestConfig:
        """Create OpenAI request configuration."""
        return OpenAIRequestConfig(
            model=self.model,
            temperature=temperature,
            tools=tools or [],
            max_retries=Constants.MAX_SURVEY_REQUESTS,
        )

    def make_json_request(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> Dict[str, Any]:
        """Make a JSON request to OpenAI."""
        result = self.handler.make_json_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=self.model,
            temperature=temperature,
        )

        if not result.success:
            raise Exception(f"Failed to get user details: {result.error}")
        return result.parsed_json

    def make_function_request(
        self, messages: list, temperature: float = 0.5, tools: list = None
    ) -> Dict[str, Any]:
        """Make a function call request to OpenAI."""
        config = self._create_request_config(temperature, tools)
        result = self.handler.make_request(
            messages, config, OpenAITools.handle_call_function
        )

        if not result.success:
            raise Exception(f"Failed to make function request: {result.error}")
        return {
            Constants.SUCCESS: result.success,
            "response_text": result.response_text,
            Constants.ERROR: result.error,
        }

    def create_messages(self, system_prompt: str, user_prompt: str) -> list:
        """Create message list for OpenAI request."""
        return [
            self.handler.create_message("system", system_prompt),
            self.handler.create_message("user", user_prompt),
        ]


class OpenAIUserDetailsManager:
    """Manages user details operations using OpenAI."""

    def __init__(self):
        self.request_handler = OpenAIDetailsRequestHandler()

    def _get_user_details_from_answers(self, answers: str, user_prompt: str) -> dict:
        """Extract user details from survey answers using OpenAI."""
        user_prompt = user_prompt.format(answers_text=answers)
        return self.request_handler.make_json_request(
            system_prompt=SystemPromptsConstants.SURVEY_ANSWERS_ASSISTANT,
            user_prompt=user_prompt,
        )

    def ask_question(self, question: str, user_input: str) -> str:
        """Validate user answer using GPT with function calling."""
        max_date = datetime.now().year
        min_date = max_date - 100

        system_prompt = SystemPromptsConstants.MEDICAL_INTAKE_ASSISTANT.format(
            min_date=min_date,
            max_date=max_date,
            no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT,
            parse_error_response=PromptsConstants.SURVEY_PARSE_ERROR,
        )
        user_prompt = PromptsConstants.SURVEY_QUESTION_PROMPT.format(
            question=question, user_input=user_input
        )

        messages = self.request_handler.create_messages(system_prompt, user_prompt)
        result = self.request_handler.make_function_request(
            messages=messages,
            temperature=0.5,
            tools=[ToolDescriptionConstants.VALIDATE_RANGE],
        )

        if result[Constants.SUCCESS] and result["response_text"]:
            return result["response_text"]
        return PromptsConstants.SURVEY_PROMPT_ERROR

    def create_user_details_from_answers(self, answers: dict, user_id: str) -> bool:
        """Create UserDetails object from survey answers and save to database."""
        try:
            details = self._get_user_details_from_answers(
                answers, PromptsConstants.SURVEY_ANSWERS_PROMPT
            )

            create_user_details(
                user_id=user_id,
                weight=float(details["weight"]),
                year_of_birth=int(details["year_of_birth"]),
                gender=details["gender"],
                allergies=details["allergies"],
            )
            return True

        except Exception as e:
            print(f"Error creating user details: {str(e)}")
            return False

    def _prepare_confirmation_prompts(
        self, current_user_data: dict, user_response: str
    ) -> Tuple[str, str]:
        """Prepare system and user prompts for confirmation."""
        max_date = datetime.now().year
        min_date = max_date - 100

        system_prompt = SystemPromptsConstants.CONFIRMATION_SYSTEM_ASSISTANT.format(
            min_date=min_date,
            max_date=max_date,
            parse_error_response=PromptsConstants.SURVEY_PARSE_ERROR,
            no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT,
            questions=Constants.QUESTIONS,
            confirm_prompt=PromptsConstants.SURVEY_CONFIRMATION_PROMPT,
        )

        user_prompt = PromptsConstants.CONFIRMATION_USER_PROMPT.format(
            current_data=current_user_data,
            user_response=user_response,
        )

        return system_prompt, user_prompt

    def _handle_special_responses(
        self, response_text: str
    ) -> Optional[UserDetailsResponse]:
        """Handle special response cases."""
        response_text = response_text.lower().strip()
        if response_text == PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT.lower():
            return UserDetailsResponse(
                success=True,
                changes={},
                error=ResponsesConstants.SURVEY_DONT_UNDERSTAND_RESPONSE,
                action=Constants.ACTION_UNCLEAR,
            )

        if response_text == PromptsConstants.SURVEY_PARSE_ERROR.lower():
            return UserDetailsResponse(
                success=True,
                changes={},
                error=ResponsesConstants.SURVEY_PARSE_ERROR_RESPONSE,
                action=Constants.ERROR,
            )

        if response_text == PromptsConstants.SURVEY_CONFIRMATION_PROMPT.lower():
            return UserDetailsResponse.success_response()

        return None

    def _process_update_request(
        self, current_user_data: dict, response_text: str
    ) -> UserDetailsResponse:
        """Process update request and return changes."""
        current_user_data_str = json.dumps(current_user_data)
        combined_text = f"""Current data: {current_user_data_str}
        Data to replace: {response_text}
        """
        details = self._get_user_details_from_answers(
            combined_text, PromptsConstants.SURVEY_ANSWERS_PROMPT_FOR_CONFIRMATION
        )

        return UserDetailsResponse.success_response(
            changes=details, action=Constants.ACTION_UPDATE
        )

    def confirm_user_details(
        self, current_user_data: dict, user_response: str
    ) -> UserDetailsResponse:
        """Process user confirmation response and return changes they want to make."""
        try:
            system_prompt, user_prompt = self._prepare_confirmation_prompts(
                current_user_data, user_response
            )
            messages = self.request_handler.create_messages(system_prompt, user_prompt)

            result = self.request_handler.make_function_request(
                messages=messages,
                temperature=0.3,
                tools=[ToolDescriptionConstants.VALIDATE_RANGE],
            )

            if not result[Constants.SUCCESS]:
                return UserDetailsResponse.error_response(
                    error=result[Constants.ERROR], action=Constants.ERROR
                )

            response_text = result["response_text"].strip()

            special_response = self._handle_special_responses(response_text)
            if special_response:
                return special_response

            return self._process_update_request(current_user_data, response_text)

        except Exception as e:
            return UserDetailsResponse.error_response(str(e))

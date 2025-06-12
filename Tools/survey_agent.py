from typing import Dict, Optional

from Constants.const import Constants
from Constants.prompts import PromptsConstants
from Constants.responses import ErrorResponsesConstants, ResponsesConstants
from Tools.openai_user_details_manager import OpenAIUserDetailsManager


class SurveyState:
    """Class to manage survey state for a user."""

    def __init__(self):
        self.current_question: int = 0
        self.answers: Dict[str, str] = {}
        self.awaiting_confirmation: bool = False
        self.survey_started: bool = False

    def update_answers(self, answers: Dict[str, str]) -> None:
        """Update answers for a user. Only updates values for existing keys.

        Args:
            answers: Dictionary of field names to new values
        """
        for key, value in answers.items():
            if key in self.answers:
                self.answers[key] = value

    def is_survey_complete(self) -> bool:
        """Check if the survey is complete."""
        return self.current_question >= len(Constants.QUESTIONS)

    def get_current_question(self) -> str:
        """Get the current question text."""
        return Constants.QUESTIONS[self.current_question]

    def get_current_field(self) -> str:
        """Get the current field name for the answer."""
        return Constants.USER_DETAILS_FIELDS[self.current_question]

    def advance_question(self) -> None:
        """Advance to the next question."""
        self.current_question += 1

    def reset(self) -> None:
        """Reset the survey state."""
        self.current_question = 0
        self.answers = {}
        self.awaiting_confirmation = False
        self.survey_started = False


class SurveyManager:
    """Manages the survey flow and state for multiple users."""

    def __init__(self):
        self._survey_states: Dict[str, SurveyState] = {}
        self._user_details_manager = OpenAIUserDetailsManager()

    def _get_survey_state(self, user_id: str) -> Optional[SurveyState]:
        """Get survey state for a user if it exists."""
        return self._survey_states.get(user_id)

    def _create_survey_state(self, user_id: str) -> SurveyState:
        """Create new survey state for a user."""
        self._survey_states[user_id] = SurveyState()
        return self._survey_states[user_id]

    def _clear_survey_state(self, user_id: str) -> None:
        """Clear survey state for a user."""
        self._survey_states.pop(user_id, None)

    def _start_survey(self, user_id: str) -> str:
        """Start a new survey for a user."""
        state = self._create_survey_state(user_id)
        state.survey_started = True
        return ResponsesConstants.SURVEY_START_RESPONSE.format(
            question=state.get_current_question()
        )

    def _repeat_survey(self, user_id: str) -> str:
        """Repeat the survey for a user."""
        state = self._create_survey_state(user_id)
        state.survey_started = True
        return ResponsesConstants.SURVEY_START_RESPONSE_AGAIN.format(
            question=state.get_current_question()
        )

    def _await_confirmation(self, state: SurveyState) -> str:
        """Await confirmation from a user."""
        state.awaiting_confirmation = True
        summary = self._format_survey_summary(state.answers)
        return ResponsesConstants.SURVEY_SUMMARY_RESPONSE.format(summary=summary)

    def _format_survey_summary(self, answers: Dict[str, str]) -> str:
        """Format survey answers into a readable summary."""
        questions = Constants.QUESTIONS
        return "\n".join(
            f"- {questions[index]} : \n\t{a}"
            for index, a in enumerate(answers.values())
        )

    def _handle_awaiting_confirmation(
        self, user_id: str, message: str, state: SurveyState
    ) -> str:
        """Handle awaiting confirmation for a user."""
        response = self._user_details_manager.confirm_user_details(
            state.answers, message
        )

        if not response.success:
            return ErrorResponsesConstants.DEBUG_ERROR_RESPONSE.format(
                error=response.error
            )

        if response.action == Constants.ACTION_UPDATE and response.changes:
            state.update_answers(response.changes.parsed_json)
            return self._await_confirmation(state)

        if response.action == Constants.ERROR:
            return response.error

        if response.action == Constants.ACTION_CONFIRM_ALL:
            success = self._user_details_manager.create_user_details_from_answers(
                state.answers, user_id
            )
            if not success:
                return ErrorResponsesConstants.ERROR_RESPONSE_SAVING_DATA

            self._clear_survey_state(user_id)
            return ResponsesConstants.SAVED_USER_DETAILS_RESPONSE

        return self._await_confirmation(state)

    def _handle_special_responses(self, response: str) -> str | None:
        """Handle special responses from the user."""
        response = response.lower().strip()

        if response == PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT.lower():
            return ResponsesConstants.SURVEY_DONT_UNDERSTAND_RESPONSE

        if response == PromptsConstants.SURVEY_PARSE_ERROR.lower():
            return ResponsesConstants.SURVEY_PARSE_ERROR_RESPONSE

        if response == PromptsConstants.SURVEY_PROMPT_ERROR.lower():
            return ResponsesConstants.SURVEY_PROMPT_ERROR_RESPONSE

        return None

    def _handle_current_question(self, message: str, state: SurveyState) -> str:
        """Handle the current question in the survey."""
        try:
            current_q = state.get_current_question()
            response = self._user_details_manager.ask_question(current_q, message)

            special_response = self._handle_special_responses(response)
            if special_response:
                return special_response

            # Save answer and move to next question
            state.answers[state.get_current_field()] = response
            state.advance_question()

            # Check if survey is complete
            if state.is_survey_complete():
                return self._await_confirmation(state)

            # Return next question
            return state.get_current_question()

        except Exception as e:
            return ErrorResponsesConstants.DEBUG_ERROR_RESPONSE.format(error=str(e))

    def process_survey_message(self, user_id: str, message: str) -> str:
        """Process a message in the survey context."""
        state = self._get_survey_state(user_id)
        if state is None:
            return self._start_survey(user_id)

        if state.awaiting_confirmation:
            return self._handle_awaiting_confirmation(user_id, message, state)

        return self._handle_current_question(message, state)

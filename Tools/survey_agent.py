from typing import Dict, Optional
from Constants.prompts import SURVEY_DONT_UNDERSTAND_PROMPT
from Tools.survey_helper import ask_question, create_user_details_from_answers
from Constants.responses import SAVED_USER_DETAILS_RESPONSE, CONFIRM_USER_DETAILS_RESPONSE, SURVEY_DONT_UNDERSTAND_RESPONSE, SURVEY_SUMMARY_RESPONSE, QUESTIONS, SURVEY_START_RESPONSE, SURVEY_START_RESPONSE_AGAIN
from Constants.error_responses import ERROR_SAVING_DATA_RESPONSE, ERROR_RESPONSE


class SurveyState:
    """Class to manage survey state for a user."""

    def __init__(self):
        self.current_question: int = 0
        self.answers: Dict[str, str] = {}
        self.awaiting_confirmation: bool = False
        self.survey_started: bool = False


class SurveyManager:

    def __init__(self):
        self._survey_states: Dict[str, SurveyState] = {}

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
        self._create_survey_state(user_id)
        return SURVEY_START_RESPONSE.format(question=QUESTIONS[0])

    def _format_survey_summary(self, answers: Dict[str, str]) -> str:
        """Format survey answers into a readable summary."""
        return "\n".join(f"- {q} : \n\t* {a}" for q, a in answers.items())

    def _handle_awaiting_confirmation(self, user_id: str, message: str, state: SurveyState) -> str:
        """Handle awaiting confirmation for a user."""
        message = message.lower().strip()
        if message == "tak":
            try:
                saved = create_user_details_from_answers(
                    state.answers, user_id)
                if saved:
                    self._clear_survey_state(user_id)
                    return SAVED_USER_DETAILS_RESPONSE
                else:
                    self._create_survey_state(user_id)
                    return ERROR_SAVING_DATA_RESPONSE.format(question=QUESTIONS[0])
            except Exception as e:
                self._create_survey_state(user_id)
                return ERROR_RESPONSE.format(error=str(e))
        elif message == "nie":
            self._create_survey_state(user_id)
            return SURVEY_START_RESPONSE_AGAIN.format(question=QUESTIONS[0])
        else:
            return CONFIRM_USER_DETAILS_RESPONSE

    def _handle_current_question(self, message: str, state: SurveyState) -> str:
        """Handle the current question in the survey"""

        try:
            current_q = QUESTIONS[state.current_question]
            response = ask_question(current_q, message)

            if response.lower() == SURVEY_DONT_UNDERSTAND_PROMPT.lower():
                return SURVEY_DONT_UNDERSTAND_RESPONSE

            # Save answer and move to next question
            state.answers[current_q] = response
            state.current_question += 1

            # Check if survey is complete
            if state.current_question >= len(QUESTIONS):
                state.awaiting_confirmation = True
                summary = self._format_survey_summary(state.answers)
                return SURVEY_SUMMARY_RESPONSE.format(summary=summary)

            # Return next question
            return QUESTIONS[state.current_question]

        except Exception as e:
            return ERROR_RESPONSE.format(error=str(e))

    def process_survey_message(self, user_id: str, message: str) -> str:
        """Process a message in the survey context"""

        state = self._get_survey_state(user_id)
        if state is None:
            return self._start_survey(user_id)

        # If awaiting confirmation
        if state.awaiting_confirmation:
            return self._handle_awaiting_confirmation(user_id, message, state)

        # Process current question
        return self._handle_current_question(message, state)

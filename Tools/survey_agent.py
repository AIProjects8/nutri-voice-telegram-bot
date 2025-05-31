from typing import Dict, Optional
from Constants.prompts import SURVEY_DONT_UNDERSTAND_PROMPT
from Tools.survey_helper import ask_question, create_user_details_from_answers


class SurveyState:
    """Class to manage survey state for a user."""

    def __init__(self):
        self.current_question: int = 0
        self.answers: Dict[str, str] = {}
        self.awaiting_confirmation: bool = False


# Survey questions
QUESTIONS = [
    "Jaka jest Twoja waga?",
    "Jaki jest Twój rok urodzenia?",
    "Jaka jest Twoja płeć?",
    "Czy masz alergie? Jeśli tak, proszę wymienić je."
]

# Store survey state for each user
survey_states: Dict[str, SurveyState] = {}


def get_survey_state(user_id: str) -> Optional[SurveyState]:
    """Get survey state for a user if it exists."""
    return survey_states.get(user_id)


def create_survey_state(user_id: str) -> SurveyState:
    """Create new survey state for a user."""
    survey_states[user_id] = SurveyState()
    return survey_states[user_id]


def clear_survey_state(user_id: str) -> None:
    """Clear survey state for a user."""
    survey_states.pop(user_id, None)


def get_or_create_survey_state(user_id: str) -> SurveyState:
    """Get or create survey state for a user."""
    state = get_survey_state(user_id)
    if state is None:
        state = create_survey_state(user_id)
    return state


def format_survey_summary(answers: Dict[str, str]) -> str:
    """Format survey answers into a readable summary."""
    return "\n".join(f"- {q} : \n\t* {a}" for q, a in answers.items())


def process_survey_message(user_id: str, message: str) -> str:
    """Process a message in the survey context"""

    state = get_survey_state(user_id)
    if state is None:
        return start_survey(user_id)

    # If awaiting confirmation
    if state.awaiting_confirmation:
        message = message.lower().strip()
        if message == "tak":
            try:
                saved = create_user_details_from_answers(
                    state.answers, user_id)
                if saved:
                    clear_survey_state(user_id)
                    return "Dziękuję! Twoje dane zostały zapisane."
                else:
                    create_survey_state(user_id)
                    return "Błąd podczas zapisywania danych. Proszę spróbować ponownie. Zacznijmy od nowa.\n\n" + QUESTIONS[0]
            except:
                create_survey_state(user_id)
                return f"Błąd podczas zapisywania danych: {str(e)}"
        elif message == "nie":
            create_survey_state(user_id)
            return "Zacznijmy od nowa.\n\n" + QUESTIONS[0]
        else:
            return "Proszę odpowiedzieć 'tak' lub 'nie'. Czy wszystkie odpowiedzi są poprawne?"

    # Process current question
    try:
        current_q = QUESTIONS[state.current_question]
        response = ask_question(current_q, message)

        if response.lower() == SURVEY_DONT_UNDERSTAND_PROMPT.lower():
            return "⚠️ Przepraszam, nie rozumiem odpowiedzi. Proszę spróbować ponownie."

        # Save answer and move to next question
        state.answers[current_q] = response
        state.current_question += 1

        # Check if survey is complete
        if state.current_question >= len(QUESTIONS):
            state.awaiting_confirmation = True
            summary = format_survey_summary(state.answers)
            return f"Oto podsumowanie Twoich odpowiedzi:\n\n{summary}\n\nCzy wszystkie odpowiedzi są poprawne? (tak/nie)"

        # Return next question
        return QUESTIONS[state.current_question]

    except Exception as e:
        return f"⚠️ Wystąpił nieoczekiwany błąd: {str(e)}"


def start_survey(user_id: str) -> str:
    """Start a new survey for a user."""
    create_survey_state(user_id)
    return f"Witaj!\n\nW celu poprawnego działania aplikacji, muszę przeprowadzić krótką ankietę.\n\nProszę odpowiedzieć na pytania.\n\n{QUESTIONS[0]}"

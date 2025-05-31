from typing import Dict
from Constants.prompts import SURVEY_DONT_UNDERSTAND_PROMPT
from Tools.survey_helper import ask_question, create_user_details_from_answers

QUESTIONS = [
    "Jaka jest Twoja waga?",
    "Jaki jest Twój rok urodzenia?",
    "Jaka jest Twoja płeć?",
    "Czy masz alergie? Jeśli tak, proszę wymienić je."
]

survey_states: Dict[str, Dict] = {}


def clear_survey_state(user_id: str) -> None:
    """Clear survey state for a user."""
    survey_states.pop(user_id, None)


def reset_survey_state(user_id: str) -> None:
    """Reset survey state for a user."""
    survey_states[user_id] = {
        'current_question': 0,
        'answers': {},
        'awaiting_confirmation': False
    }


def get_or_create_survey_state(user_id: str) -> Dict:
    """Get or create survey state for a user."""
    if user_id not in survey_states:
        reset_survey_state(user_id)
    return survey_states[user_id]


def start_survey(user_id: str) -> str:
    get_or_create_survey_state(user_id)
    return f"Witaj!\n\nW celu poprawnego działania aplikacji, muszę przeprowadzić krótką ankietę.\n\nProszę odpowiedzieć na pytania.\n\n{QUESTIONS[0]}"


def is_survey_started(user_id: str) -> bool:
    return user_id in survey_states


def process_survey_message(user_id: str, message: str) -> str:
    """Process a message in the survey context"""

    if not is_survey_started(user_id):
        return start_survey(user_id)

    state = get_or_create_survey_state(user_id)

    # If awaiting confirmation
    if state['awaiting_confirmation']:
        message = message.lower().strip()
        if message == "tak":
            try:
                saved = create_user_details_from_answers(
                    state['answers'], user_id)
                if saved:
                    # Clear survey state
                    clear_survey_state(user_id)
                    return "Dziękuję! Twoje dane zostały zapisane."
                else:
                    reset_survey_state(user_id)
                    return "Błąd podczas zapisywania danych. Proszę spróbować ponownie. Zacznijmy od nowa.\n\n" + QUESTIONS[0]
            except Exception as e:
                return f"Błąd podczas zapisywania danych: {str(e)}"
        elif message == "nie":
            # Reset survey
            reset_survey_state(user_id)
            return "Zacznijmy od nowa.\n\n" + QUESTIONS[0]
        else:
            return "Proszę odpowiedzieć 'tak' lub 'nie'. Czy wszystkie odpowiedzi są poprawne?"

    # Process current question
    current_q = QUESTIONS[state['current_question']]
    response = ask_question(current_q, message)

    if response.lower() == SURVEY_DONT_UNDERSTAND_PROMPT.lower():
        return "⚠️ Przepraszam, nie rozumiem odpowiedzi. Proszę spróbować ponownie."

    # Save answer and move to next question
    state['answers'][current_q] = response
    state['current_question'] += 1

    # Check if survey is complete
    if state['current_question'] >= len(QUESTIONS):
        state['awaiting_confirmation'] = True
        summary = "\n".join(f"- {q} : \n\t* {a}" for q,
                            a in state['answers'].items())
        return f"Oto podsumowanie Twoich odpowiedzi:\n\n{summary}\n\nCzy wszystkie odpowiedzi są poprawne? (tak/nie)"

    # Return next question
    return QUESTIONS[state['current_question']]

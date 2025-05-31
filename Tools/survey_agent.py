from openai import OpenAI
import os
from typing import Dict
from SqlDB.user_details_service import create_details
from SqlDB.database import get_db
from datetime import datetime
from Constants.prompts import CHAT_MAIN_PROMPT
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

QUESTIONS = [
    "Jaka jest Twoja waga?",
    "Jaki jest Twój rok urodzenia?",
    "Jaki jest Twój płeć?",
    "Czy masz alergie? Jeśli tak, proszę wymienić je. Jeśli nie, powiedz 'nie'."
]

# Store survey state for each user
survey_states: Dict[str, Dict] = {}


def save_user_details(user_id: str, weight: float, year_of_birth: int, gender: str, allergies: str) -> None:
    """Save user details to the database.

    Args:
        user_id: The user's ID
        weight: User's weight in kilograms
        year_of_birth: User's year of birth
        gender: User's gender (M/K)
        allergies: User's allergies as a comma-separated string
    """
    db = next(get_db())
    create_details(
        db=db,
        user_id=user_id,
        weight=weight,
        year_of_birth=year_of_birth,
        gender=gender,
        allergies=allergies
    )


def get_or_create_survey_state(user_id: str) -> Dict:
    """Get or create survey state for a user."""
    if user_id not in survey_states:
        survey_states[user_id] = {
            'current_question': 0,
            'answers': {},
            'awaiting_confirmation': False
        }
    return survey_states[user_id]


def ask_question(question: str, user_input: str) -> str:
    """Ask a question and validate the answer using GPT."""
    prompt = f"""
{CHAT_MAIN_PROMPT} User was asked: "{question}"
If the answer is unclear, return only "nie rozumiem".
If question is about year of birth, return only the year in format YYYY. User can use YY or YYYY format.
If question is about weight, return only the weight in float format.
If question is about allergies, return only the allergies separated by commas. Example: 'jabłko, orzechy, jaja'.
If question is about gender, return only 'M' for male or 'K' for female.

User can reply in Polish.
The user reply is "{user_input}"
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a medical intake assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def create_user_details_from_answers(answers: dict, user_id: str) -> None:
    """Create UserDetails object from survey answers and save to database."""
    answers_text = "\n".join(f"{q}: {a}" for q, a in answers.items())

    # Define the function schema
    functions = [{
        "type": "function",
        "function": {
            "name": "save_user_details",
            "description": "Save user details to the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID"
                    },
                    "weight": {
                        "type": "number",
                        "description": "User's weight in kilograms"
                    },
                    "year_of_birth": {
                        "type": "integer",
                        "description": "User's year of birth"
                    },
                    "gender": {
                        "type": "string",
                        "description": "User's gender (M/K)",
                        "enum": ["M", "K"]
                    },
                    "allergies": {
                        "type": "string",
                        "description": "User's allergies as a comma-separated string"
                    }
                },
                "required": ["user_id", "weight", "year_of_birth", "gender", "allergies"]
            }
        }
    }]

    prompt = f"""
{CHAT_MAIN_PROMPT}

Given the following survey answers, extract these values and use the save_user_details function to save them:
- weight (number)
- year_of_birth (number)
- gender
- allergies (string)

Rules:
- Normalize gender to "M" or "K"
- Allergies should be a string separated by commas
- If any answer is empty or unclear, use null
- Weight should be a float number
- Year of birth should be a 4-digit number

Survey answers:
{answers_text}

Call the save_user_details function with the extracted values.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data normalization assistant."},
            {"role": "user", "content": prompt}
        ],
        tools=functions,
        tool_choice={"type": "function", "function": {
            "name": "save_user_details"}},
        temperature=0
    )

    # Get the function call from the response
    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        if tool_call.function.name == "save_user_details":
            try:
                # Parse the arguments
                args = json.loads(tool_call.function.arguments)

                # Validate the arguments
                if not isinstance(args["weight"], (int, float)):
                    raise ValueError("Weight must be a number")
                if not isinstance(args["year_of_birth"], int):
                    raise ValueError("Year of birth must be an integer")
                if args["gender"] not in ["M", "K"]:
                    raise ValueError("Gender must be 'M' or 'K'")

                # Call the function with the parsed arguments
                save_user_details(
                    user_id=user_id,  # Use the provided user_id instead of args
                    weight=float(args["weight"]),
                    year_of_birth=int(args["year_of_birth"]),
                    gender=args["gender"],
                    allergies=args["allergies"]
                )
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in function arguments")
            except KeyError as e:
                raise ValueError(f"Missing required argument: {e}")
            except Exception as e:
                raise ValueError(
                    f"Error processing function arguments: {str(e)}")
    else:
        raise ValueError("No function call in the response")


def process_survey_message(user_id: str, message: str) -> str:
    """Process a message in the survey contextt"""

    if not is_survey_started(user_id):
        return start_survey(user_id)

    state = get_or_create_survey_state(user_id)

    # If awaiting confirmation
    if state['awaiting_confirmation']:
        if message.lower() in ['tak', 't']:
            try:
                create_user_details_from_answers(state['answers'], user_id)
                # Clear survey state
                survey_states.pop(user_id, None)
                return "Dziękuję! Twoje dane zostały zapisane."
            except Exception as e:
                return f"Błąd podczas zapisywania danych: {str(e)}"
        elif message.lower() in ['nie', 'n']:
            # Reset survey
            state['current_question'] = 0
            state['answers'] = {}
            state['awaiting_confirmation'] = False
            return "Zacznijmy od nowa.\n\n" + QUESTIONS[0]
        else:
            return "Proszę odpowiedzieć 'tak' lub 'nie'. Czy wszystkie odpowiedzi są poprawne?"

    # Process current question
    current_q = QUESTIONS[state['current_question']]
    response = ask_question(current_q, message)

    if response.lower() == "nie rozumiem":
        return "⚠️ Przepraszam, nie rozumiem odpowiedzi. Proszę spróbować ponownie. ⚠️"

    # Save answer and move to next question
    state['answers'][current_q] = response
    state['current_question'] += 1

    # Check if survey is complete
    if state['current_question'] >= len(QUESTIONS):
        state['awaiting_confirmation'] = True
        summary = "\n".join(f"- {q} → {a}" for q,
                            a in state['answers'].items())
        return f"Oto podsumowanie Twoich odpowiedzi:\n\n{summary}\n\nCzy wszystkie odpowiedzi są poprawne? (tak/nie)"

    # Return next question
    return QUESTIONS[state['current_question']]


def start_survey(user_id: str) -> str:
    get_or_create_survey_state(user_id)
    return f"Witaj!\n\nW celu poprawnego działania aplikacji, muszę przeprowadzić krótką ankietę.\n\nProszę odpowiedzieć na pytania.\n\n{QUESTIONS[0]}"


def is_survey_started(user_id: str) -> bool:
    return user_id in survey_states

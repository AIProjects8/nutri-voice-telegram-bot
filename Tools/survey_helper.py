import json
from Constants.prompts import CHAT_MAIN_PROMPT, SURVEY_QUESTION_PROMPT
from Tools.openai_tools import OpenAIClient
from SqlDB.user_details_service import create_user_details
from config import Config


def ask_question(question: str, user_input: str) -> str:
    """Validate the user answer using GPT."""
    prompt = f"""
{CHAT_MAIN_PROMPT} User was asked: "{question}"

{SURVEY_QUESTION_PROMPT}
Question: {question}
User answer: {user_input}
"""

    response = OpenAIClient.get_instance().client.chat.completions.create(
        model=Config.from_env().gpt_model,
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

    prompt = f"""
Extract user details from these survey answers and return as JSON:
{answers_text}

Required format:
{{
    "user_id": "{user_id}",
    "weight": <number>,
    "year_of_birth": <integer>,
    "gender": "M" or "K",
    "allergies": "<comma-separated string or empty>"
}}
"""
    response = OpenAIClient.get_instance().client.chat.completions.create(
        model=Config.from_env().gpt_model,
        messages=[
            {"role": "system", "content": "Extract user details and return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    details = json.loads(response.choices[0].message.content.strip())

    try:
        create_user_details(
            user_id=user_id,
            weight=float(details["weight"]),
            year_of_birth=int(details["year_of_birth"]),
            gender=details["gender"],
            allergies=details["allergies"]
        )
        return True
    except:
        return False

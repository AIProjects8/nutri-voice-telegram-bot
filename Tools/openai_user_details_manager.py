import json
from Constants.prompts import PromptsConstants, SystemPromptsConstants
from Tools.openai_tools import OpenAIClient
from SqlDB.user_details_service import create_user_details
from config import Config


class OpenAIUserDetailsManager:
    def __init__(self):
        self.client = OpenAIClient.get_instance().client

    def _get_user_details_from_answers(self, answers: dict, user_id: str) -> dict:
        answers_text = "\n".join(f"{q}: {a}" for q, a in answers.items())
        prompt = PromptsConstants.SURVEY_ANSWERS_PROMPT.format(
            answers_text=answers_text, user_id=user_id
        )

        response = OpenAIClient.get_instance().client.chat.completions.create(
            model=Config.from_env().gpt_model,
            messages=[
                {"role": "system",
                    "content": SystemPromptsConstants.SURVEY_ANSWERS_ASSISTANT},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return json.loads(response.choices[0].message.content.strip())

    def ask_question(self, question: str, user_input: str) -> str:
        """Validate the user answer using GPT."""
        prompt = f"""
    {PromptsConstants.CHAT_MAIN_PROMPT} User was asked: "{question}"

    {PromptsConstants.SURVEY_QUESTION_PROMPT}
    Question: {question}
    User answer: {user_input}
    """

        response = self.client.chat.completions.create(
            model=Config.from_env().gpt_model,
            messages=[
                {"role": "system",
                    "content": SystemPromptsConstants.MEDICAL_INTAKE_ASSISTANT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    def create_user_details_from_answers(self, answers: dict, user_id: str) -> None:
        """Create UserDetails object from survey answers and save to database."""
        details = self._get_user_details_from_answers(answers, user_id)

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

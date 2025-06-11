from config import Config
from Constants.prompts import (
    ALREADY_REGISTERED_MESSAGE,
    REGISTRATION_AGENT_PROMPT,
    REGISTRATION_WELCOME_MESSAGE,
)
from models import User
from Tools.database_manager import DatabaseManager

from .base_agent import BaseAgent
from .context import AgentContext
from .interview_engine import InterviewEngine


class UserRegistrationAgent(BaseAgent):
    def __init__(self):
        config = Config.from_env()
        super().__init__(
            name="User Registration Agent",
            instructions=REGISTRATION_AGENT_PROMPT,
            model=config.agent_model,
        )
        self.db = DatabaseManager()

    def registration_flow(self, user_message: str, context: AgentContext) -> str:
        user_id = context.user_id

        if self.is_user_registered(user_id):
            return ALREADY_REGISTERED_MESSAGE

        if not InterviewEngine._states.get(user_id):
            next_question = InterviewEngine.get_next_question(user_id)
            return REGISTRATION_WELCOME_MESSAGE.format(question=next_question)

        is_completed, response = InterviewEngine.process_answer(user_id, user_message)

        if is_completed:
            user_data = InterviewEngine.get_collected_data(user_id)
            self._save_user_data(user_id, user_data)
            InterviewEngine.clear_state(user_id)
            return f"{response}\n\n Registration complete! You can now use the full functionality of NutriBot."

        return response

    def _save_user_data(self, user_id: int, data: dict):
        user = User(
            user_id=user_id,
            name=data.get("name"),
            age=data.get("age"),
            weight=data.get("weight"),
            height=data.get("height"),
            allergies=data.get("allergies", []),
            registration_completed=True,
        )
        self.db.create_user(user)

    def get_capabilities(self) -> list[str]:
        return ["user_registration", "data_collection", "onboarding"]

    def is_user_registered(self, user_id: int) -> bool:
        user = self.db.get_user(user_id)
        return user is not None and user.registration_completed


def create_user_registration_agent() -> UserRegistrationAgent:
    return UserRegistrationAgent()

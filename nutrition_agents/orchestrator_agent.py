from agents import Agent, ModelSettings
from config import Config

from .base_agent import BaseAgent
from .context import AgentContext


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        config = Config.from_env()
        super().__init__(
            name="NutriBot Orchestrator",
            instructions="You are the main agent of a diet app. You help users track their diet and symptoms. Answer very concisely and avoid unnecessary words.",
            model=config.agent_model,
        )

    def create_agent(self) -> Agent:
        config = Config.from_env()
        return Agent[AgentContext](
            name=self.name,
            instructions=self.instructions,
            model=self.model,
            model_settings=ModelSettings(
                temperature=config.model_temperature,
            ),
        )

    def get_capabilities(self) -> list[str]:
        return ["diet_tracking", "symptom_tracking", "general_nutrition_advice"]


def create_orchestrator_agent() -> OrchestratorAgent:
    return OrchestratorAgent()

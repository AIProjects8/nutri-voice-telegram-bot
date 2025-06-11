from typing import Any

from agents import Agent

from .context import AgentContext


class BaseAgent:
    def __init__(self, name: str, instructions: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.instructions = instructions
        self.model = model
        self._agent = None

    @property
    def agent(self) -> Agent:
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent

    def create_agent(self) -> Agent:
        return Agent[AgentContext](
            name=self.name, instructions=self.instructions, model=self.model
        )

    def get_capabilities(self) -> list[str]:
        return []

import openai

from config import Config
from Constants.tools import ToolsConstants


class OpenAIClient:
    _instance = None
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if OpenAIClient._client is None:
            config = Config.from_env()
            OpenAIClient._client = openai.OpenAI(api_key=config.openai_api_key)

    @property
    def client(self):
        return self._client


class OpenAITools:

    def validate_range(value: int | float, min_value: int | float, max_value: int | float) -> bool:
        """Validates if a value is within the specified range."""
        return min_value <= value <= max_value

    def handle_validate_range(args: dict) -> bool:
        """Handle validate range tool call."""

        result = OpenAITools.validate_range(
            value=args["value"],
            min_value=args["min_value"],
            max_value=args["max_value"]
        )

        return result

    def handle_call_function(name: str, args: dict) -> str:
        """Handle tool calls from the response."""
        if name == ToolsConstants.VALIDATE_RANGE:
            return OpenAITools.handle_validate_range(args)
        else:
            return f"Tool call not supported"

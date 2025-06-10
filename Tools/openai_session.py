import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall

from config import Config
from Constants.const import Constants
from Tools.openai_tools import OpenAIClient


@dataclass
class OpenAIMessage:
    """Represents a message in the OpenAI conversation."""

    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format."""
        return {"role": self.role, "content": self.content}


@dataclass
class OpenAIRequestConfig:
    """Configuration for OpenAI API requests with automatic defaults."""

    model: Optional[str] = None
    temperature: Optional[float] = None
    tools: Optional[List[Dict]] = None
    max_retries: Optional[int] = None

    def __post_init__(self):
        """Apply defaults for None values after initialization."""
        if self.model is None:
            self.model = Config.from_env().gpt_model
        if self.temperature is None:
            self.temperature = Constants.DEFAULT_TEMPERATURE
        if self.max_retries is None:
            self.max_retries = Constants.DEFAULT_MAX_REQUESTS


class OpenAIResponse:
    """Represents a response from OpenAI API."""

    def __init__(
        self,
        success: bool,
        response_text: Optional[str] = None,
        full_response: Any = None,
        error: Optional[str] = None,
        parsed_json: Optional[Dict] = None,
    ):
        self.success = success
        self.response_text = response_text
        self.full_response = full_response
        self.error = error
        self.parsed_json = parsed_json

    @classmethod
    def success(
        cls,
        response_text: str,
        full_response: Any = None,
        parsed_json: Optional[Dict] = None,
    ) -> "OpenAIResponse":
        """Create a successful response."""
        return cls(True, response_text, full_response, None, parsed_json)

    @classmethod
    def error(cls, error: str) -> "OpenAIResponse":
        """Create an error response."""
        return cls(False, None, None, error, None)


class GeneralOpenAIHandler:
    """A general-purpose handler for OpenAI API requests with optional function calling support."""

    def __init__(self):
        self.client = OpenAIClient.get_instance().client

    def create_message(self, role: str, content: str) -> OpenAIMessage:
        """Create a properly formatted message."""
        return OpenAIMessage(role=role, content=content)

    def _execute_function_calls(
        self,
        function_calls: List[ResponseFunctionToolCall],
        messages: List[Dict],
        function_handler: callable,
    ) -> None:
        """Execute function calls and append results to message history."""
        for tool_call in function_calls:
            if tool_call.type != "function_call":
                continue

            try:
                function_name = tool_call.name
                function_args = json.loads(tool_call.arguments)
                result = function_handler(function_name, function_args)

                messages.append(tool_call)
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(result),
                    }
                )

            except Exception as e:
                messages.append(tool_call)
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": f"Error executing function: {str(e)}",
                    }
                )

    def _format_messages(
        self, messages: List[Union[OpenAIMessage, Dict]]
    ) -> List[Dict]:
        """Format messages for API request."""
        return [
            msg.to_dict() if isinstance(msg, OpenAIMessage) else msg for msg in messages
        ]

    def _prepare_request_params(
        self, config: OpenAIRequestConfig, formatted_messages: List[Dict]
    ) -> Dict[str, Any]:
        """Prepare request parameters for API call."""
        params = {
            "model": config.model,
            "input": formatted_messages,
            "temperature": config.temperature,
        }

        if config.tools:
            params["tools"] = config.tools

        return params

    def _make_request(
        self,
        messages: List[Union[OpenAIMessage, Dict]],
        config: OpenAIRequestConfig,
        function_handler: Optional[callable] = None,
    ) -> OpenAIResponse:
        """Make a general OpenAI request with optional function calling."""
        formatted_messages = self._format_messages(messages)
        request_params = self._prepare_request_params(config, formatted_messages)

        for attempt in range(config.max_retries):
            try:
                response = self.client.responses.create(**request_params)

                if response.output and function_handler:
                    self._execute_function_calls(
                        response.output, formatted_messages, function_handler
                    )

                if not response.output_text:
                    continue

                return OpenAIResponse.success(
                    response_text=response.output_text, full_response=response
                )

            except Exception as e:
                if attempt == config.max_retries - 1:
                    return OpenAIResponse.error(str(e))
                continue

        return OpenAIResponse.error("Osiagnieto maksymalna liczbe prob")

    def _prepare_messages(
        self, system_prompt: str, user_prompt: str
    ) -> List[OpenAIMessage]:
        """Prepare messages for API request."""
        return [
            self.create_message("system", system_prompt),
            self.create_message("user", user_prompt),
        ]

    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """Parse JSON from response content."""
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}")

    def make_function_request(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict],
        function_handler: callable,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: int = Constants.DEFAULT_MAX_FUNCTION_REQUESTS,
    ) -> OpenAIResponse:
        """Make a request with function calling."""
        if not tools or not function_handler:
            return self.make_simple_request(
                system_prompt, user_prompt, model, temperature
            )

        messages = self._prepare_messages(system_prompt, user_prompt)

        config = OpenAIRequestConfig(
            model=model,
            temperature=temperature,
            tools=tools,
            max_retries=max_retries,
        )

        return self._make_request(messages, config, function_handler)

    def make_simple_request(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> OpenAIResponse:
        """Make a simple request without function calling."""
        messages = self._prepare_messages(system_prompt, user_prompt)

        config = OpenAIRequestConfig(
            model=model,
            temperature=temperature,
            max_retries=max_retries,
        )

        return self._make_request(messages, config)

    def make_json_request(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> OpenAIResponse:
        """Make a request expecting JSON response and parse it."""
        result = self.make_simple_request(
            system_prompt, user_prompt, model, temperature, max_retries
        )

        if result.success and result.response_text:
            try:
                parsed_json = self._parse_json_response(result.response_text)
                return OpenAIResponse.success(
                    response_text=result.response_text,
                    full_response=result.full_response,
                    parsed_json=parsed_json,
                )
            except ValueError as e:
                return OpenAIResponse.error(str(e))

        return result

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
import json
from Constants.settings import SettingsConstants
from Tools.openai_tools import OpenAIClient


@dataclass
class OpenAIMessage:
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class OpenAIRequestConfig:
    model: str
    temperature: float = SettingsConstants.DEFAULT_TEMPERATURE
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict]] = None
    max_retries: int = SettingsConstants.DEFAULT_MAX_REQUESTS


class GeneralOpenAIHandler:
    """
    A general-purpose handler for OpenAI API requests with optional function calling support.
    """

    def __init__(self):
        self.client = OpenAIClient.get_instance().client

    def create_message(self, role: str, content: str) -> OpenAIMessage:
        """Helper method to create properly formatted messages."""
        return OpenAIMessage(role=role, content=content)

    def _execute_function_calls(self,
                                function_calls: List[ResponseFunctionToolCall],
                                messages: List[Dict],
                                function_handler: callable) -> None:
        """
        Execute function calls and append results to message history.

        Args:
            function_calls: List of function calls from OpenAI response
            messages: Message history to append to
            function_handler: Function to handle the actual function execution
        """
        for tool_call in function_calls:
            if tool_call.type != "function_call":
                continue

            try:
                function_name = tool_call.name
                function_args = json.loads(tool_call.arguments)

                result = function_handler(function_name, function_args)

                messages.append(tool_call)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result)
                })

            except Exception as e:
                messages.append(tool_call)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": f"Error executing function: {str(e)}"
                })

    def make_request(self,
                     messages: List[Union[OpenAIMessage, Dict]],
                     config: OpenAIRequestConfig,
                     function_handler: Optional[callable] = None) -> Dict[str, Any]:
        """
        Make a general OpenAI request with optional function calling.

        Args:
            messages: List of messages (can be OpenAIMessage objects or dicts)
            config: Configuration for the request
            function_handler: Optional function to handle function calls

        Returns:
            Dict containing success status, response text, and any errors
        """
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, OpenAIMessage):
                formatted_messages.append(msg.to_dict())
            else:
                formatted_messages.append(msg)

        # Prepare request parameters
        request_params = {
            "model": config.model,
            "input": formatted_messages,
            "temperature": config.temperature
        }

        if config.max_tokens:
            request_params["max_tokens"] = config.max_tokens
        if config.tools:
            request_params["tools"] = config.tools

        # Attempt the request with retries
        for attempt in range(config.max_retries):
            try:
                response = self.client.responses.create(**request_params)

                # Handle function calls if present and handler provided
                if response.output and function_handler:
                    self._execute_function_calls(
                        response.output,
                        formatted_messages,
                        function_handler
                    )

                if not response.output_text:
                    continue

                return {
                    "success": True,
                    "response_text": response.output_text,
                    "full_response": response,
                    "error": None
                }

            except Exception as e:
                if attempt == config.max_retries - 1:  # Last attempt
                    return {
                        "success": False,
                        "response_text": None,
                        "full_response": None,
                        "error": str(e)
                    }
                continue

        return {
            "success": False,
            "response_text": None,
            "full_response": None,
            "error": "Max retries exceeded"
        }

    def make_simple_request(self,
                            system_prompt: str,
                            user_prompt: str,
                            model: str,
                            temperature: float = 0.0) -> Dict[str, Any]:
        """
        Simplified method for basic requests without function calling.

        Args:
            system_prompt: System message content
            user_prompt: User message content  
            model: Model to use
            temperature: Temperature setting

        Returns:
            Dict containing success status and response
        """
        messages = [
            self.create_message("system", system_prompt),
            self.create_message("user", user_prompt)
        ]

        config = OpenAIRequestConfig(
            model=model,
            temperature=temperature,
        )

        return self.make_request(messages, config)

    def make_json_request(self,
                          system_prompt: str,
                          user_prompt: str,
                          model: str,
                          temperature: float = 0.0) -> Dict[str, Any]:
        """
        Make a request expecting JSON response and parse it.

        Args:
            system_prompt: System message content
            user_prompt: User message content
            model: Model to use  
            temperature: Temperature setting

        Returns:
            Dict containing success status, parsed JSON, and any errors
        """
        result = self.make_simple_request(
            system_prompt, user_prompt, model, temperature)

        if result["success"] and result["response_text"]:
            try:
                content = result["response_text"].strip()
                if content.startswith('```json'):
                    content = content[7:]  # Remove ```json
                if content.endswith('```'):
                    content = content[:-3]  # Remove trailing ```
                content = content.strip()  # Remove any extra whitespace
                parsed_json = json.loads(content)
                result["parsed_json"] = parsed_json
            except json.JSONDecodeError as e:
                result["success"] = False
                result["error"] = f"Failed to parse JSON response: {str(e)}"
                result["parsed_json"] = None
        else:
            result["parsed_json"] = None

        return result

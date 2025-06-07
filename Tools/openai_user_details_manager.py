import json
from datetime import datetime
from Constants.tools import ToolDescriptionConstants
from Constants.prompts import PromptsConstants, SystemPromptsConstants
from Tools.openai_tools import OpenAIClient, OpenAITools
from SqlDB.user_details_service import create_user_details
from config import Config
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall


class OpenAIUserDetailsManager:
    def __init__(self):
        self.client = OpenAIClient.get_instance().client

    def _get_user_details_from_answers(self, answers: dict, user_id: str) -> dict:
        answers_text = "\n".join(f"{q}: {a}" for q, a in answers.items())
        prompt = PromptsConstants.SURVEY_ANSWERS_PROMPT.format(
            answers_text=answers_text, user_id=user_id
        )

        response = self.client.responses.create(
            model=Config.from_env().gpt_model,
            input=[
                {"role": "system",
                    "content": SystemPromptsConstants.SURVEY_ANSWERS_ASSISTANT},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return json.loads(response.output_text)

    def _execute_tool_calls(self, output: list[ResponseFunctionToolCall], input_messages: list) -> str:
        """Execute tool calls from the response."""
        for tool_call in output:
            if tool_call.type != "function_call":
                continue
            name = tool_call.name
            args = json.loads(tool_call.arguments)
            result = OpenAITools.handle_call_function(name, args)
            input_messages.append(tool_call)
            input_messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })

    def ask_question(self, question: str, user_input: str) -> str:
        """Validate the user answer using GPT."""
        max_date = datetime.now().year
        min_date = max_date - 100
        prompt = PromptsConstants.SURVEY_QUESTION_PROMPT.format(
            question=question, user_input=user_input)

        input_messages = [
            {"role": "system",
             "content": SystemPromptsConstants.MEDICAL_INTAKE_ASSISTANT.format(
                 min_date=min_date, max_date=max_date, no_answer_response=PromptsConstants.SURVEY_DONT_UNDERSTAND_PROMPT)},
            {"role": "user", "content": prompt}
        ]
        MAX_ATTEMPTS = 3
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            try:
                response = self.client.responses.create(
                    model=Config.from_env().gpt_model,
                    input=input_messages,
                    temperature=0.5,
                    tools=[ToolDescriptionConstants.VALIDATE_RANGE]
                )
                self._execute_tool_calls(response.output, input_messages)

            except Exception as e:
                return PromptsConstants.SURVEY_PROMPT_ERROR
            if response.output_text:
                return response.output_text
        return PromptsConstants.SURVEY_PROMPT_ERROR

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

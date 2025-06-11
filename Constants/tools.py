class ToolsConstants:
    VALIDATE_RANGE = "validate_range"


class ToolDescriptionConstants:
    VALIDATE_RANGE = {
        "type": "function",
        "name": ToolsConstants.VALIDATE_RANGE,
        "description": "Validates if a number is within a specified range",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "The number to validate (float or integer)",
                },
                "min_value": {
                    "type": "number",
                    "description": "Minimum allowed number (float or integer)",
                },
                "max_value": {
                    "type": "number",
                    "description": "Maximum allowed number (float or integer)",
                },
            },
            "required": ["value", "min_value", "max_value"],
            "additionalProperties": False,
        },
        "strict": True,
    }

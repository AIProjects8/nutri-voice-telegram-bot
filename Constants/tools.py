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
                    "description": "The number to validate (float or integer)"
                },
                "min_value": {
                    "type": "number",
                    "description": "Minimum allowed number (float or integer)"
                },
                "max_value": {
                    "type": "number",
                    "description": "Maximum allowed number (float or integer)"
                }
            },
            "required": ["value", "min_value", "max_value"],
            "additionalProperties": False
        },
        "strict": True
    }
    # UPDATE_QUESTION = {
    #     "type": "function",
    #     "name": ToolsConstants.UPDATE_QUESTION,
    #     "description": "Update question with new value provided by user",
    #     "parameters": {
    #         "type": "object",
    #             "properties": {
    #                 "user_id": {
    #                     "type": "string",
    #                     "description": "The unique identifier of the user (UUID or database ID)."
    #                 },
    #                 "question": {
    #                     "type": "string",
    #                     "description": "Name of the question/field to be updated (e.g. 'weight', 'year_of_birth', 'gender', 'allergies')"
    #                 },
    #                 "new_value": {
    #                     "type": "string",
    #                     "description": "New value provided by user"
    #                 }
    #             },
    #         "required": ["question", "new_value"],
    #         "additionalProperties": False
    #     },
    #     "strict": True
    # }
    # CREATE_USER_DETAILS = {
    #     "type": "function",
    #     "name": ToolsConstants.CREATE_USER_DETAILS,
    #     "description": "Create a user details entry in the database using answers provided from a survey.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "user_id": {
    #                 "type": "string",
    #                 "description": "The unique identifier of the user (UUID or database ID)."
    #             },
    #             "answers": {
    #                 "type": "object",
    #                 "description": "Survey answers from the user used to extract user details.",
    #                 "properties": {
    #                     "weight": {
    #                         "type": "string",
    #                         "description": "User's weight in kilograms (e.g., '70')."
    #                     },
    #                     "year_of_birth": {
    #                         "type": "string",
    #                         "description": "User's year of birth (e.g., '1995')."
    #                     },
    #                     "gender": {
    #                         "type": "string",
    #                         "description": "User's gender (e.g., 'male', 'female', 'non-binary')."
    #                     },
    #                     "allergies": {
    #                         "type": "string",
    #                         "description": "List of user's allergies separated by commas (e.g., 'gluten, lactose')."
    #                     }
    #                 },
    #                 "required": ["weight", "year_of_birth", "gender", "allergies"],
    #                 "additionalProperties": False
    #             }
    #         },
    #         "required": ["user_id", "answers"],
    #         "additionalProperties": False
    #     },
    #     "strict": True
    # }

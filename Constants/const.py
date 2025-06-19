class Constants:
    DEFAULT_TEMPERATURE = 0.0
    DEFAULT_MAX_REQUESTS = 1
    DEFAULT_MAX_FUNCTION_REQUESTS = 2

    USER_DETAILS_FIELDS = ["weight", "year_of_birth", "gender", "allergies"]
    # Survey questions
    QUESTIONS = [
        "Jaka jest Twoja waga?",
        "Jaki jest Twój rok urodzenia?",
        "Jaka jest Twoja płeć?",
        "Czy masz alergie? Jeśli tak, proszę wymienić je.",
    ]

    ERROR = "error"
    SUCCESS = "success"
    CHANGES = "changes"
    ACTION = "action"
    ACTION_UPDATE = "update"
    ACTION_CONFIRM_ALL = "confirm_all"
    ACTION_UNCLEAR = "unclear"

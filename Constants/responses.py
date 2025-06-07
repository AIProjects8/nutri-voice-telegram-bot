class ResponsesConstants:

    SAVED_USER_DETAILS_RESPONSE = "Dziękuję! Twoje dane zostały zapisane."
    CONFIRM_USER_DETAILS_RESPONSE = "Proszę odpowiedzieć 'tak' lub 'nie'. Czy wszystkie odpowiedzi są poprawne?"
    SURVEY_DONT_UNDERSTAND_RESPONSE = "⚠️ Przepraszam, nie rozumiem odpowiedzi. Proszę spróbować ponownie."
    SURVEY_SUMMARY_RESPONSE = "Oto podsumowanie Twoich odpowiedzi:\n\n{summary}\n\nCzy wszystkie odpowiedzi są poprawne? (tak/nie)"
    SURVEY_START_RESPONSE = """
Witaj!

W celu poprawnego działania aplikacji, muszę przeprowadzić krótką ankietę.
Proszę odpowiedzieć na pytania.

{question}
"""
    SURVEY_PROMPT_ERROR_RESPONSE = "⚠️ Przepraszam, wystąpił błąd podczas przetwarzania odpowiedzi. Proszę spróbować ponownie."
    SURVEY_PARSE_ERROR_RESPONSE = "⚠️ Odpowiedź jest niedozwolona. Proszę spróbować ponownie."
    SURVEY_START_RESPONSE_AGAIN = """
Zacznijmy od nowa.

{question}
"""
# Survey questions
    QUESTIONS = [
        "Jaka jest Twoja waga?",
        "Jaki jest Twój rok urodzenia?",
        "Jaka jest Twoja płeć?",
        "Czy masz alergie? Jeśli tak, proszę wymienić je."
    ]


class ErrorResponsesConstants:

    ERROR_RESPONSE_SAVING_DATA = "Wystąpił nieoczekiwany błąd podczas zapisywania danych."
    ERROR_RESPONSE_PROCESS = "Wystąpił nieoczekiwany błąd podczas przetwarzania odpowiedzi."
    DEBUG_ERROR_RESPONSE = "Wystąpił nieoczekiwany błąd podczas przetwarzania odpowiedzi. {error}"
    ERROR_SAVING_DATA_RESPONSE = """
Wystąpił błąd podczas zapisywania danych.
Proszę spróbować ponownie.

{question}
"""

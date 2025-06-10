class ResponsesConstants:
    """Responses constants for the survey agent."""

    SAVED_USER_DETAILS_RESPONSE = "Dziękuję! Twoje dane zostały zapisane."
    SURVEY_DONT_UNDERSTAND_RESPONSE = (
        "⚠️ Przepraszam, nie rozumiem odpowiedzi. Proszę spróbować ponownie."
    )
    SURVEY_SUMMARY_RESPONSE = "Oto podsumowanie Twoich odpowiedzi:\n\n{summary}\n\nCzy wszystkie odpowiedzi są poprawne? (Jeśli nie, opisz co chcesz zmienić)"
    SURVEY_START_RESPONSE = """
Witaj!

W celu poprawnego działania aplikacji, muszę przeprowadzić krótką ankietę.
Proszę odpowiedzieć na pytania.

{question}
"""
    SURVEY_PROMPT_ERROR_RESPONSE = "⚠️ Przepraszam, wystąpił błąd podczas przetwarzania odpowiedzi. Proszę spróbować ponownie."
    SURVEY_PARSE_ERROR_RESPONSE = (
        "⚠️ Odpowiedź spoza dozwolonego zakresu. Proszę spróbować ponownie."
    )
    SURVEY_START_RESPONSE_AGAIN = """
Zacznijmy od nowa.

{question}
"""


class ErrorResponsesConstants:

    ERROR_RESPONSE_SAVING_DATA = (
        "Wystąpił nieoczekiwany błąd podczas zapisywania danych."
    )
    ERROR_RESPONSE_PROCESS = (
        "Wystąpił nieoczekiwany błąd podczas przetwarzania odpowiedzi."
    )
    DEBUG_ERROR_RESPONSE = (
        "Wystąpił nieoczekiwany błąd podczas przetwarzania odpowiedzi. {error}"
    )
    ERROR_SAVING_DATA_RESPONSE = """
Wystąpił błąd podczas zapisywania danych.
Proszę spróbować ponownie.

{question}
"""

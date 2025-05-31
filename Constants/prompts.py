from datetime import datetime

CHAT_MAIN_PROMPT = 'You are a helpful assistant. Always respond in Polish language.'

SURVEY_DONT_UNDERSTAND_PROMPT = "NIE_ROZUMIEM"

SURVEY_QUESTION_PROMPT = f"""
Try to find the answer to the question and return in the specified format.

BIRTH YEAR QUESTION:
- Return only the year in YYYY format
- Birth year should be between {datetime.now().year - 100} and {datetime.now().year}
- Require 4 digits year format from the user answer

WEIGHT QUESTION:
- Return only the weight in kg (number only)
- User weight should be between 10 kg and 200 kg
- By default user unit is kg
- Weigh can be a float number with one decimal place

ALLERGIES QUESTION:
- Find allergies and return them separated by commas. Example: 'milk, nuts, eggs'
- If user has no allergies, return: nie

GENDER QUESTION:
- Return only: 'Mężczyzna' or 'Kobieta'
- Accept various forms for male/female

Return exactly: {SURVEY_DONT_UNDERSTAND_PROMPT} if:
- User doesn't know the answer
- User answer is not clear
- User answer cannot be processed
- Answer is outside valid range
- You cannot extract meaningful information

Process the answer according to the rules above.
"""

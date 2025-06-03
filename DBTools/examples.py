from datetime import datetime
import data_tools as dt

# Example: Insert a single ingredient document
ingredient_doc = {
    "ingredients": [
        "nori (seaweed)",
        "sushi rice",
        "salmon",
        "fish filling (unidentified)",
        "wasabi",
        "pickled ginger (gari)"
    ],
    "userId": 12345,
    "timestamp": datetime.fromisoformat("2025-04-06T14:32:00"),
    "Summary": "Six maki sushi rolls with two fillings, wasabi, and gari."
}

ingredient_id = dt.insert_ingredient(ingredient_doc)
print(f"Inserted ingredient with ID: {ingredient_id}")

# Example: Insert multiple user documents
user_docs = [
    {
        "id": 12345,
        "age": 30,
        "sex": "male",
        "weight": 72.5,
        "known_issues": ["allergic to nuts"]
    },
    {
        "id": 67890,
        "age": 25,
        "sex": "female",
        "weight": 60.0,
        "known_issues": []
    }
]

user_ids = dt.insert_users(user_docs)
print(f"Inserted users with IDs: {user_ids}")

# Example: Insert a single symptom document
symptom_doc = {
    "summary": "Mild nausea and itching after eating sushi",
    "timestamp": datetime.fromisoformat("2025-04-06T15:00:00"),
    "userId": 12345
}

symptom_id = dt.insert_symptom(symptom_doc)
print(f"Inserted symptom with ID: {symptom_id}")

# Example: Insert multiple symptoms
symptom_docs = [
    {
        "summary": "Headache after breakfast",
        "timestamp": datetime.now(),
        "userId": 67890
    },
    {
        "summary": "Fatigue after lunch",
        "timestamp": datetime.now(),
        "userId": 12345
    }
]

symptom_ids = dt.insert_symptoms(symptom_docs)
print(f"Inserted symptoms with IDs: {symptom_ids}")

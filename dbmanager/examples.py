from datetime import datetime
#from dbmanager import db  # Direct collection access
from dbmanager import data_tools as dt


if __name__ == "__main__":
    # Example: Insert a single meal document
    meal_doc = {
        "ingredients": [
            "nori (seaweed)",
            "sushi rice",
            "salmon",
            "fish filling (unidentified)",
            "wasabi",
            "pickled ginger (gari)"
        ],
        "userId": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": datetime.fromisoformat("2025-04-06T14:32:00"),
        "Summary": "Six maki sushi rolls with two fillings, wasabi, and gari."
    }

    meal_id = dt.insert_meal(meal_doc)
    print(f"Inserted meal with ID: {meal_id}")

    # Example: Insert multiple user documents
    user_docs = [
        {
            "userId": "550e8400-e29b-41d4-a716-446655440011",
            "age": 30,
            "sex": "blob",
            "weight": 72.5,
            "allergies": ["allergic to nuts"]
        },
        {
            "userId": "550e8400-e29b-41d4-a716-446655440022",
            "yearOfBirth": 1995,
            "gender": "female",
            "weight": 100.343,
            "allergies": [],
            "health_issues": []
        },
        {
            "userId": "550e8400-e29b-41d4-a716-446655440000",
            "yearOfBirth": 1990,
            "gender": "female",
            "weight": 60.0,
            "allergies": [],
            "health_issues": []
        }   
    ]

    user_ids = dt.insert_users(user_docs)
    print(f"Inserted users with IDs: {user_ids}")

    # Example: Insert a single symptom document
    symptom_doc = {
        "summary": "Mild nausea and itching after eating sushi",
        "timestamp": datetime.fromisoformat("2025-04-06T15:00:00"),
        "userId": "550e8400-e29b-41d4-a716-446655440000",
    }

    symptom_id = dt.insert_symptom(symptom_doc)
    print(f"Inserted symptom with ID: {symptom_id}")

    # Example: Insert multiple symptoms
    symptom_docs = [
        {
            "summary": "Headache after breakfast",
            "timestamp": datetime.now(),
            "userId": "550e8400-e29b-41d4-a716-446655440022",
        },
        {
            "summary": "Fatigue after lunch",
            "timestamp": datetime.now(),
            "userId": "550e8400-e29b-41d4-a716-446655440000",
        },

    ]

    symptom_ids = dt.insert_symptoms(symptom_docs)
    print(f"Inserted symptoms with IDs: {symptom_ids}")

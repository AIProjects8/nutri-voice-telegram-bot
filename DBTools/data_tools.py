from pymongo.errors import PyMongoError
from pydantic import ValidationError
from typing import List, Dict, Any

from models import MealCollection, UsersCollection, SymptomsCollection
from mongodb import db

def insert_meal(document: Dict[str, Any]) -> str:
    """Validate and insert a single meal document."""
    try:
        validated = MealCollection(**document)
        result = db.meals.insert_one(validated.model_dump())
        return str(result.inserted_id)
    except ValidationError as e:
        print(f"Validation error (meal): {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error (meal): {e}")
        raise

def insert_meals(documents: List[Dict[str, Any]]) -> List[str]:
    """Validate and insert multiple meals documents."""
    ids = []
    for doc in documents:
        ids.append(insert_meal(doc))
    return ids

def insert_user(document: Dict[str, Any]) -> str:
    """Validate and insert a single user document."""
    try:
        validated = UsersCollection(**document)
        result = db.users.insert_one(validated.model_dump())
        return str(result.inserted_id)
    except ValidationError as e:
        print(f"Validation error (user): {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error (user): {e}")
        raise

def insert_users(documents: List[Dict[str, Any]]) -> List[str]:
    """Validate and insert multiple user documents."""
    ids = []
    for doc in documents:
        ids.append(insert_user(doc))
    return ids

def insert_symptom(document: Dict[str, Any]) -> str:
    """Validate and insert a single symptom document."""
    try:
        validated = SymptomsCollection(**document)
        result = db.symptoms.insert_one(validated.model_dump())
        return str(result.inserted_id)
    except ValidationError as e:
        print(f"Validation error (symptom): {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error (symptom): {e}")
        raise

def insert_symptoms(documents: List[Dict[str, Any]]) -> List[str]:
    """Validate and insert multiple symptom documents."""
    ids = []
    for doc in documents:
        ids.append(insert_symptom(doc))
    return ids

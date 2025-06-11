from typing import Any, Dict, List, Optional

from pydantic import ValidationError
from pymongo.errors import PyMongoError

from . import db
from .models import MealCollection, SymptomsCollection, UserDetailsCollection


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


def insert_user_details(document: Dict[str, Any]) -> str:
    """Validate and insert a single user document."""
    try:
        validated = UserDetailsCollection(**document)
        result = db.users.insert_one(validated.model_dump())
        return str(result.inserted_id)
    except ValidationError as e:
        print(f"Validation error (user): {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error (user): {e}")
        raise


def insert_users_details(documents: List[Dict[str, Any]]) -> List[str]:
    """Validate and insert multiple user documents."""
    ids = []
    for doc in documents:
        ids.append(insert_user_details(doc))
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


def get_user_details(user_id: str) -> Optional[UserDetailsCollection]:
    """Retrieve validated user details from MongoDB"""
    try:
        if user_doc := db.users.find_one({"userId": user_id}):
            return UserDetailsCollection(**user_doc)
        return None
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        raise


def get_user_details_json(user_id: str) -> Optional[dict]:
    """Retrieve user details from MongoDB and return as JSON structure"""
    try:
        user_doc = db.users.find_one({"userId": user_id})
        if user_doc:
            validated = UserDetailsCollection(**user_doc)
            return validated.model_dump()
        return None
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        raise


def has_user_details(user_id: str) -> bool:
    """Check existence of user details in MongoDB"""
    try:
        return db.users.find_one({"userId": user_id}) is not None
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        raise

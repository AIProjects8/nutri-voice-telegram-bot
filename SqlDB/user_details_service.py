from sqlalchemy.orm import Session, class_mapper

from .database import get_db
from .models import UserDetails


def create_user_details(user_id: str, weight: float, year_of_birth: int, gender: str, allergies: str) -> UserDetails:
    """Save user details to the database."""
    db = next(get_db())
    user_details = UserDetails(user_id=user_id, weight=weight,
                               year_of_birth=year_of_birth, gender=gender, allergies=allergies)
    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return user_details


def get_user_details(user_id: str) -> UserDetails | None:
    db = next(get_db())
    return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()


def has_user_details(db: Session, user_id: str) -> bool:
    db = next(get_db())
    return db.query(UserDetails).filter(UserDetails.user_id == user_id).first() is not None

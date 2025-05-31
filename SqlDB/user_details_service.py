from sqlalchemy.orm import Session
from .models import UserDetails
from .database import get_db


def create_details(db: Session, user_id: str, weight: float, year_of_birth: int, gender: str, allergies: str) -> UserDetails:
    user_details = UserDetails(user_id=user_id, weight=weight,
                               year_of_birth=year_of_birth, gender=gender, allergies=allergies)
    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return user_details


def get_user_details_by_user_id(db: Session, user_id: str) -> UserDetails | None:
    return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()


def is_user_details_exists(db: Session, user_id: str) -> bool:
    return db.query(UserDetails).filter(UserDetails.user_id == user_id).first() is not None


def save_user_details(user_id: str, weight: float, year_of_birth: int, gender: str, allergies: str) -> None:
    """Save user details to the database."""

    db = next(get_db())
    create_details(
        db=db,
        user_id=user_id,
        weight=weight,
        year_of_birth=year_of_birth,
        gender=gender,
        allergies=allergies
    )

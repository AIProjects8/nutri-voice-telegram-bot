from sqlalchemy.orm import Session
from .models import User

def user_exists(db: Session, telegram_id: int) -> bool:
    return db.query(User).filter(User.telegram_id == telegram_id).first() is not None 
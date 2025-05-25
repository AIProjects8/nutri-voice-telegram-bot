from telegram import Update
from telegram.ext import ContextTypes
from .database import get_db
from .user_service import get_user_by_telegram_id, create_user
from .cache import UserCache

async def user_middleware(update: Update) -> bool:
    if not update.effective_user:
        return False
        
    telegram_id = update.effective_user.id
    cache = UserCache()
    
    if cache.has_user(telegram_id):
        return True
        
    db = next(get_db())
    try:
        user = get_user_by_telegram_id(db, telegram_id)
        if not user:
            user = create_user(db, telegram_id)
        cache.add_user(telegram_id, user)
        return True
    finally:
        db.close() 
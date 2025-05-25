from telegram import Update
from telegram.ext import ContextTypes
from .database import get_db
from .user_service import user_exists

async def user_exists_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.effective_user:
        return False
        
    telegram_id = update.effective_user.id
    db = next(get_db())
    
    try:
        return user_exists(db, telegram_id)
    finally:
        db.close() 
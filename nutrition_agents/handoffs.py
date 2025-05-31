from typing import Optional, Dict, Any
from .context import AgentContext
from Tools.database_manager import DatabaseManager

class AgentCoordinator:
    
    @staticmethod
    def should_handoff_to_registration(context: AgentContext) -> bool:
        db_manager = DatabaseManager()
        if not db_manager.user_exists(context.user_id):
            return True
        
        user = db_manager.get_user(context.user_id)
        return user is None or not user.registration_completed
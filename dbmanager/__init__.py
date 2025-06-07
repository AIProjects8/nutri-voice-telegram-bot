from pathlib import Path
from .mongo_manager import MongoDBManager

required_collections = ["users", "meals", "symptoms"]
required_indexes = {
    "meals": [ [("userId", 1)], [("timestamp", 1)] ],                
    "users": [ [("userId", 1)] ],
    "symptoms": [ [("userId", 1)], [("timestamp", 1)] ]
}

# Cross-platform .env path resolution
# Safely get .env file from the main project directory
env_path = Path(__file__).parent.parent / ".env"

# Central manager instance
_db_manager = MongoDBManager(
    required_collections, 
    required_indexes, 
    env_path=str(env_path)
)

# Unified access point for collections
class DB:
    @property
    def users(self):
        return _db_manager.db["users"]
    
    @property
    def meals(self):
        return _db_manager.db["meals"]
    
    @property
    def symptoms(self):
        return _db_manager.db["symptoms"]

# Expose db_manager at the package level
db = DB()
__all__ = ["db", "MongoDBManager"]

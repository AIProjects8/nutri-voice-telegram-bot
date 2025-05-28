from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional, Dict, Any
from config import Config
from models import User
from datetime import datetime

class DatabaseManager:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if DatabaseManager._client is None:
            config = Config.from_env()
            DatabaseManager._client = MongoClient(config.mongodb_uri)
            DatabaseManager._db = DatabaseManager._client[config.mongodb_database]

    @property
    def users(self) -> Collection:
        return self._db.users

    @property
    def meals(self) -> Collection:
        return self._db.meals

    @property
    def symptoms(self) -> Collection:
        return self._db.symptoms

    def get_user(self, user_id: int) -> Optional[User]:
        user_data = self.users.find_one({"user_id": user_id})
        if user_data:
            user_data.pop("_id", None)
            return User(**user_data)
        return None

    def create_user(self, user: User) -> User:
        user_dict = user.model_dump()
        self.users.insert_one(user_dict)
        return user

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[User]:
        updates["updated_at"] = datetime.now()
        result = self.users.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )
        if result.modified_count > 0:
            return self.get_user(user_id)
        return None

    def user_exists(self, user_id: int) -> bool:
        return self.users.find_one({"user_id": user_id}) is not None

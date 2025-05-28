from typing import Dict, Optional
from .models import User

class UserCache:
    _instance = None
    _cache: Dict[int, User] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_user(self, telegram_id: int) -> Optional[User]:
        return self._cache.get(telegram_id)

    def add_user(self, telegram_id: int, user: User) -> None:
        self._cache[telegram_id] = user

    def has_user(self, telegram_id: int) -> bool:
        return telegram_id in self._cache 
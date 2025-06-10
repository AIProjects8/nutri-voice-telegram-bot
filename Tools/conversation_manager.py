from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

from SqlDB.user_cache import UserCache


@dataclass
class Message:
    role: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    timestamp: datetime


class ConversationManager:
    _instance = None
    _conversations: Dict[str, List[Message]] = {}
    _max_history: int = 10

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationManager, cls).__new__(cls)
        return cls._instance

    def _validate_user_id(self, user_id: str) -> None:
        if not user_id:
            raise ValueError("User ID cannot be empty")

    def add_message(
        self,
        user_id: str,
        role: str,
        content: Union[str, Dict[str, Any], List[Dict[str, Any]]],
    ) -> None:
        self._validate_user_id(user_id)

        if user_id not in self._conversations:
            self._conversations[user_id] = []

        message = Message(role=role, content=content, timestamp=datetime.now())

        self._conversations[user_id].append(message)

        if len(self._conversations[user_id]) > self._max_history:
            self._conversations[user_id] = self._conversations[user_id][
                -self._max_history :
            ]

    def get_conversation_history(self, user_id: str) -> List[dict]:
        self._validate_user_id(user_id)

        if user_id not in self._conversations:
            return []

        return [
            {"role": msg.role, "content": msg.content}
            for msg in self._conversations[user_id]
        ]

    def clear_history(self, user_id: str) -> None:
        self._validate_user_id(user_id)

        if user_id in self._conversations:
            self._conversations[user_id] = []

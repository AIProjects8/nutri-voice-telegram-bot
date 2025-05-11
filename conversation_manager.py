from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime

class ConversationManager:
    _instance = None
    _conversations: Dict[int, List[Message]] = {}
    _max_history: int = 10
    _system_message: dict = {
        "role": "system",
        "content": "You are a helpful assistant. Always respond in Polish language."
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationManager, cls).__new__(cls)
        return cls._instance

    def add_message(self, user_id: int, role: str, content: str) -> None:
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        self._conversations[user_id].append(message)
        
        if len(self._conversations[user_id]) > self._max_history:
            self._conversations[user_id] = self._conversations[user_id][-self._max_history:]

    def get_conversation_history(self, user_id: int) -> List[dict]:
        if user_id not in self._conversations:
            return [self._system_message]
        
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self._conversations[user_id]
        ]
        
        return [self._system_message] + messages

    def clear_history(self, user_id: int) -> None:
        if user_id in self._conversations:
            self._conversations[user_id] = [] 
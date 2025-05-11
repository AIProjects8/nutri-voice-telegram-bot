from typing import Dict, List, Union, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    role: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    timestamp: datetime

class ConversationManager:
    _instance = None
    _conversations: Dict[int, List[Message]] = {}
    _max_history: int = 10

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationManager, cls).__new__(cls)
        return cls._instance

    def add_message(self, user_id: int, role: str, content: Union[str, Dict[str, Any], List[Dict[str, Any]]]) -> None:
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
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self._conversations[user_id]
        ]
        
        return messages

    def clear_history(self, user_id: int) -> None:
        if user_id in self._conversations:
            self._conversations[user_id] = [] 
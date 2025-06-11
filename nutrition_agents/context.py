from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AgentContext:
    user_id: int
    session_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.session_data is None:
            self.session_data = {}

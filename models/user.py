from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class User(BaseModel):
    user_id: int = Field(..., description="Telegram user ID")
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    weight: Optional[float] = Field(None, ge=20.0, le=300.0, description="Weight in kg")
    height: Optional[int] = Field(None, ge=50, le=250, description="Height in cm")
    allergies: List[str] = Field(default_factory=list)
    health_goals: List[str] = Field(default_factory=list)
    registration_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

class IngredientsCollection(BaseModel):
    ingredients: List[str] = Field(..., description="List of food ingredients")
    userId: int = Field(..., description="Telegram user ID")
    timestamp: datetime = Field(..., description="When the meal was recorded")
    Summary: str = Field(..., description="Description of the meal")

    model_config = ConfigDict(
        str_max_length=10000,
        json_schema_extra={
            "example": {
                "ingredients": [
                    "nori (seaweed)",
                    "sushi rice",
                    "salmon",
                    "fish filling (unidentified)",
                    "wasabi",
                    "pickled ginger (gari)"
                ],
                "userId": 12345,
                "timestamp": "2025-04-06T14:32:00Z",
                "Summary": "Six maki sushi rolls with two fillings, wasabi, and gari."
            }
        }
    )

class UsersCollection(BaseModel):
    id: int = Field(..., description="Telegram user ID")
    internal_id: str = Field(default_factory=lambda: str(uuid4()), description="Generated GUID when not exists")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")
    sex: Optional[str] = Field(
        None, 
        pattern="^(male|female|other)$",  # <-- use pattern instead of regex
        description="User gender"
    )
    weight: Optional[float] = Field(None, gt=0, description="User weight in kg")
    known_issues: List[str] = Field(default_factory=list, description="Known allergies or health issues")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 12345,
                "internal_id": "550e8400-e29b-41d4-a716-446655440000",
                "age": 30,
                "sex": "male",
                "weight": 72.5,
                "known_issues": ["allergic to nuts"]
            }
        }
    )

class SymptomsCollection(BaseModel):
    summary: str = Field(..., description="Description of symptoms experienced")
    timestamp: datetime = Field(..., description="When symptoms were recorded")
    userId: int = Field(..., description="Telegram user ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "Mild nausea and itching after eating sushi",
                "timestamp": "2025-04-06T15:00:00Z",
                "userId": 12345
            }
        }
    )


# Optional: Combined validator for all collections
#class NutriVoiceSchemas:
#    ingredients = IngredientsCollection
#    users = UsersCollection
#    symptoms = SymptomsCollection

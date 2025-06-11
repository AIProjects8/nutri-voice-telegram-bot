from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MealCollection(BaseModel):
    ingredients: List[str] = Field(..., description="List of food ingredients")
    userId: str = Field(..., description="Internal UserID")
    timestamp: datetime = Field(..., description="When the meal was recorded")
    Summary: str = Field(..., description="Description of the meal")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ingredients": [
                    "nori (seaweed)",
                    "sushi rice",
                    "salmon",
                    "fish filling (unidentified)",
                    "wasabi",
                    "pickled ginger (gari)",
                ],
                "userId": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-04-06T14:32:00Z",
                "Summary": "Six maki sushi rolls with two fillings, wasabi, and gari.",
            }
        }
    )


class UserDetailsCollection(BaseModel):
    userId: str = Field(..., description="Internal UserID")
    yearOfBirth: Optional[int] = Field(
        None,
        ge=1900,
        description="Year of birth (must be a four-digit year, not in the future)",
    )
    gender: Optional[str] = Field(
        None,
        pattern="^(male|female|other)$",  # <-- use pattern instead of regex
        description="User gender",
    )
    weight: Optional[float] = Field(None, gt=0, description="User weight in kg")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    health_issues: List[str] = Field(
        default_factory=list, description="Known  health issues"
    )

    @field_validator("yearOfBirth")
    @classmethod
    def check_year(cls, v):
        if v is None:
            return v
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Year of birth cannot be in the future (>{current_year})")
        if not (1000 <= v <= 9999):
            raise ValueError("Year of birth must be a four-digit integer")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "userId": "550e8400-e29b-41d4-a716-446655440000",
                "yearOfBirth": 1990,
                "gender": "male",
                "weight": 72.5,
                "allergies": ["allergic to nuts"],
                "health_issues": ["sensitive to gluten"],
            }
        }
    )


class SymptomsCollection(BaseModel):
    summary: str = Field(..., description="Description of symptoms experienced")
    timestamp: datetime = Field(..., description="When symptoms were recorded")
    userId: str = Field(..., description="Internal UserID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "Mild nausea and itching after eating sushi",
                "timestamp": "2025-04-06T15:00:00Z",
                "userId": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )

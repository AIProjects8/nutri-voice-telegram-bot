from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from Constants.prompts import REGISTRATION_QUESTIONS, REGISTRATION_COMPLETION_MESSAGE, REGISTRATION_ERROR_MESSAGE

class RegistrationStep(Enum):
    NAME = "name"
    AGE = "age"
    WEIGHT = "weight"
    HEIGHT = "height"
    ALLERGIES = "allergies"
    COMPLETED = "completed"

@dataclass
class InterviewState:
    user_id: int
    current_step: RegistrationStep
    collected_data: Dict[str, Any]
    
    def __post_init__(self):
        if self.collected_data is None:
            self.collected_data = {}

class InterviewEngine:
    _states: Dict[int, InterviewState] = {}
    
    STEP_ORDER = [
        RegistrationStep.NAME,
        RegistrationStep.AGE,
        RegistrationStep.WEIGHT,
        RegistrationStep.HEIGHT,
        RegistrationStep.ALLERGIES,
        RegistrationStep.COMPLETED
    ]
    
    QUESTIONS = {
        RegistrationStep.NAME: REGISTRATION_QUESTIONS["name"],
        RegistrationStep.AGE: REGISTRATION_QUESTIONS["age"],
        RegistrationStep.WEIGHT: REGISTRATION_QUESTIONS["weight"],
        RegistrationStep.HEIGHT: REGISTRATION_QUESTIONS["height"],
        RegistrationStep.ALLERGIES: REGISTRATION_QUESTIONS["allergies"],
    }

    @classmethod
    def get_state(cls, user_id: int) -> InterviewState:
        if user_id not in cls._states:
            cls._states[user_id] = InterviewState(
                user_id=user_id,
                current_step=RegistrationStep.NAME,
                collected_data={}
            )
        return cls._states[user_id]

    @classmethod
    def get_next_question(cls, user_id: int) -> Optional[str]:
        state = cls.get_state(user_id)
        if state.current_step in cls.QUESTIONS:
            return cls.QUESTIONS[state.current_step]
        return None

    @classmethod
    def process_answer(cls, user_id: int, answer: str) -> tuple[bool, Optional[str]]:
        state = cls.get_state(user_id)
        
        field_name = state.current_step.value
        processed_value = cls._process_field_value(state.current_step, answer)
        
        if processed_value is not None:
            state.collected_data[field_name] = processed_value
            cls._advance_step(state)
            
            if state.current_step == RegistrationStep.COMPLETED:
                return True, REGISTRATION_COMPLETION_MESSAGE
            else:
                next_question = cls.get_next_question(user_id)
                return False, next_question
        else:
            return False, REGISTRATION_ERROR_MESSAGE.format(question=cls.QUESTIONS[state.current_step])

    @classmethod
    def _process_field_value(cls, step: RegistrationStep, value: str) -> Any:
        try:
            if step == RegistrationStep.NAME:
                return value.strip()
            elif step == RegistrationStep.AGE:
                age = int(value)
                return age if 1 <= age <= 120 else None
            elif step == RegistrationStep.WEIGHT:
                weight = float(value.replace(',', '.'))
                return weight if 20.0 <= weight <= 300.0 else None
            elif step == RegistrationStep.HEIGHT:
                height = int(value)
                return height if 50 <= height <= 250 else None
            elif step == RegistrationStep.ALLERGIES:
                if value.lower() in ['no', 'none', 'nie', 'brak']:
                    return []
                return [allergy.strip() for allergy in value.split(',')]
        except (ValueError, TypeError):
            return None
        return value

    @classmethod
    def _advance_step(cls, state: InterviewState):
        current_index = cls.STEP_ORDER.index(state.current_step)
        if current_index < len(cls.STEP_ORDER) - 1:
            state.current_step = cls.STEP_ORDER[current_index + 1]

    @classmethod
    def is_completed(cls, user_id: int) -> bool:
        state = cls.get_state(user_id)
        return state.current_step == RegistrationStep.COMPLETED

    @classmethod
    def get_collected_data(cls, user_id: int) -> Dict[str, Any]:
        state = cls.get_state(user_id)
        return state.collected_data.copy()

    @classmethod
    def clear_state(cls, user_id: int):
        if user_id in cls._states:
            del cls._states[user_id]

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ConsultationCreate(BaseModel):
    problem_description: str

class ConsultationResponse(BaseModel):
    id: int
    problem_description: str
    ai_recommendation: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProgressEntryCreate(BaseModel):
    consultation_id: int
    description: str
    mood_rating: float
    symptoms_improved: str

class ProgressEntryResponse(BaseModel):
    id: int
    date: datetime
    description: str
    mood_rating: float
    symptoms_improved: str
    ai_feedback: str
    
    class Config:
        from_attributes = True
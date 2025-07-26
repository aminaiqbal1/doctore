from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    consultations = relationship("Consultation", back_populates="user")
    progress_entries = relationship("ProgressEntry", back_populates="user")

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_description = Column(Text)
    ai_recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="consultations")

class ProgressEntry(Base):
    __tablename__ = "progress_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    consultation_id = Column(Integer, ForeignKey("consultations.id"))
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    mood_rating = Column(Float)
    symptoms_improved = Column(Text)
    ai_feedback = Column(Text)
    
    user = relationship("User", back_populates="progress_entries")
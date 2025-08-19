from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Use the application's Base defined in database.py so all models share the same metadata
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, unique=False, index=True, nullable=False)
    chat_history = relationship("ChatHistory", back_populates="user")
    patients = relationship("Patient", back_populates="user")


class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patient.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="chat_history")
    patient = relationship("Patient", back_populates="chat_history")


class Patient(Base):
    __tablename__ = 'patient'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=True, nullable=False)
    age = Column(Integer, unique=False, index=True, nullable=False)
    gender = Column(String, unique=False, index=True, nullable=False)
    address = Column(String, unique=False, index=True, nullable=False)
    medical_histories = relationship("MedicalHistory", back_populates="patient")
    chat_history = relationship("ChatHistory", back_populates="patient")
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="patients")
    progress = relationship("Progress", back_populates="patient", cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__ = 'doctors' 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, index=True, nullable=False)
    age = Column(Integer, unique=False, index=True, nullable=False)
    gender = Column(String, unique=False, index=True, nullable=False)
    address = Column(String, unique=False, index=True, nullable=False)


class MedicalHistory(Base):
    __tablename__ = 'medical_histories' 

    id = Column(Integer, primary_key=True, index=True)
    diagnosis = Column(String, index=True)
    treatment = Column(String, unique=False, index=True, nullable=False)
    allergies = Column(String, unique=False, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey('patient.id')) 

    patient = relationship("Patient", back_populates="medical_histories")


class Progress(Base):
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True, index=True)
    current_status = Column(String, index=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))

    patient = relationship("Patient", back_populates="progress")

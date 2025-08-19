# C:/langgraph/doctor_agent/schemas.py

from pydantic import BaseModel
from typing import List
from typing_extensions import TypedDict


# ================== User Schemas ==================
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True


# ================== Core Data Schemas ==================
# These are the base schemas with shared fields.

class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    address: str

class MedicalHistoryBase(BaseModel):
    diagnosis: str
    treatment: str
    allergies: str


# ================== Creation Schemas ==================
# Use these for request bodies when creating new items.

class PatientCreate(PatientBase):
    pass

class MedicalHistoryCreate(MedicalHistoryBase):
    patient_id: int


# ================== Response Schemas ==================
# Use these for API responses to display data. This is where we fix the loop.

# A simple response for a Medical History record (without the patient object)
class MedicalHistory(MedicalHistoryBase):
    id: int

    # for pydantic v2:
    model_config = {"from_attributes": True}

# A simple response for a Patient (without their medical history)
class Patient(PatientBase):
    id: int

    model_config = {"from_attributes": True}

# --- Schemas for Nested Responses ---

# Use this to show a Patient AND their full medical history
class PatientWithHistory(Patient):
    medical_histories: List[MedicalHistory] = []

# Use this to show a Medical History record AND the patient it belongs to
class MedicalHistoryWithPatient(MedicalHistory):
    patient: Patient


# ================== Doctor Schemas (ADD THESE IF MISSING) ==================
class DoctorBase(BaseModel):
    name: str
    age: int
    gender: str
    address: str
    # Add any other fields specific to a Doctor

class DoctorCreate(DoctorBase):
    pass # No additional fields needed for creation beyond base

class Doctor(DoctorBase):
    id: int # Doctors will have an ID when retrieved from the DB

    model_config = {"from_attributes": True}

# ================== Progress Schemas (ADD THESE IF MISSING) ==================
class ProgressBase(BaseModel):
    current_status: str
    # Add any other fields relevant to patient progress (e.g., patient_id, date, etc.)

class ProgressCreate(ProgressBase):
    pass # No additional fields needed for creation beyond base

class Progress(ProgressBase):
    id: int # Progress records will have an ID when retrieved from the DB

    model_config = {"from_attributes": True}


# ================== State for Agent ==================
class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str
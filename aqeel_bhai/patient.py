# routers/views.py - Your original, correct version regarding 'schems'

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sqlalchemy as sa
from pydantic import BaseModel
from typing import Union

# IMPORTANT: Import your schemas and your SQLAlchemy models
import schems  # ensure this module exists; adjust name if your file is 'schemas.py'
from table import Patient, Doctor, Progress
# Import your database session and AI components
from database import get_db, sql_agent_executor, SessionLocal  # SessionLocal used in fallback
from servises.llms import groq_llm 

router = APIRouter(prefix="/profile", tags=["profile"])

# Pydantic model for the natural language query endpoint
class NaturalLanguageQuery(BaseModel):
    question: str

# Pydantic model for the response, allowing for a flexible answer type
class AgentQueryResponse(BaseModel):
    question: str
    answer: Union[str, int, float, None]


@router.post("/patient", response_model=schems.Patient)
def patient_profile(patient: schems.PatientCreate, db: Session = Depends(get_db)):
    """
    Creates a patient profile.
    - `patient: schems.PatientCreate` validates the incoming request body.
    - `response_model=schems.Patient` formats the outgoing response.
    """
    try:
        # Create a SQLAlchemy Patient model instance from Pydantic data
        db_patient = Patient(
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            address=patient.address,
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback() # Purpose: DB transaction ko undo karne ke liye.# Use case: Agar koi error ya exception aajaye aur commit ho chuka nahi ho.
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/doctor", response_model=schems.Doctor)
def doctor_profile(doctor: schems.DoctorCreate, db: Session = Depends(get_db)):
    """
    Creates a doctor profile.
    - `doctor: schems.DoctorCreate` validates the incoming request body.
    - `response_model=schems.Doctor` formats the outgoing response.
    """
    try:
        # Use .model_dump() to easily pass Pydantic data to SQLAlchemy model
        db_doctor = Doctor(doctor.model_dump())
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback() # Rollback in case of database error
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/progress", response_model=schems.Progress)
def progress_tracker(progress: schems.ProgressCreate, db: Session = Depends(get_db)):
    """
    Tracks patient progress.
    - `progress: schems.ProgressCreate` validates the incoming request body.
    - `response_model=schems.Progress` formats the outgoing response.
    """
    try:
        # use double-splat to pass dict -> SQLAlchemy model
        db_progress = Progress(progress.model_dump())
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress
    except Exception as e:
        db.rollback() # Rollback in case of database error
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recommendation")
def recommendation(progress: schems.ProgressCreate):
    """
    Generates a medical recommendation based on patient status using Groq LLM.
    """
    try:
        prompt = f"Based on the following patient status, suggest a suitable medical recommendation: {progress.current_status}"
        result = groq_llm.invoke(prompt)
        # LLM result might need parsing. We assume 'content' attribute for this example.
        recommendation_text = getattr(result, 'content', str(result))
        return {"message": "Recommendation generated", "recommendation": recommendation_text}
    except Exception as e:
        # Changed status code to 500 for internal server errors from LLM
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")


@router.post("/query-database", response_model=AgentQueryResponse) # Updated response_model
def query_database(query: NaturalLanguageQuery):
    """
    Accepts a natural language question and queries the database using the SQL agent.
    If the agent fails to provide a direct numerical answer for simple counts,
    a fallback mechanism for counting patients is applied.
    """
    print("\n--- Invoking SQL Agent ---")
    print(f"Question: {query.question}")

    try:
        # The agent is invoked with the user's question.
        # It returns a dictionary, with the final answer in the "output" key.
        agent_raw_result = sql_agent_executor.invoke({"input": query.question})
        print("SQL Agent Executor Raw Result:", agent_raw_result)

        agent_output = agent_raw_result.get("output")

        # Attempt to parse the agent's output as an integer
        try:
            final_answer = int(agent_output)
            print(f"Agent successfully returned a numeric answer: {final_answer}")
            return {"question": query.question, "answer": final_answer}
        except (ValueError, TypeError):
            # If the agent's output is not a direct number, it's likely its thought process.
            # In this specific case, for "how many patients", we can implement a fallback.
            print(f"Agent did not return a direct number. Its output was: '{agent_output}'")
            if "how many patients" in query.question.lower() or "count patients" in query.question.lower():
                # Fallback: Attempt to directly count patients if the agent's output is not direct
                print("Attempting fallback to direct patient count.")
                try:
                    db_session = SessionLocal()
                    # Execute a direct SQL query to count patients
                    # Ensure your 'patient' table exists and is correctly named
                    count_result = db_session.execute(sa.text("SELECT COUNT(*) FROM patient")).scalar_one()
                    db_session.close() # Close the session
                    print(f"Fallback successful. Found {count_result} patients.")
                    return {"question": query.question, "answer": count_result}
                except Exception as db_e:
                    print(f"Fallback failed during direct database query: {db_e}")
                    # If fallback fails, return the agent's original descriptive output
                    return {"question": query.question, "answer": agent_output}
            else:
                # For other queries where the agent doesn't return a direct number,
                # just return the agent's descriptive output.
                return {"question": query.question, "answer": agent_output}

    except Exception as e:
        # If the agent fails, return an error
        print(f"An unexpected error occurred during /query-database: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying database: {str(e)}")



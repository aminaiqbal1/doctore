from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session #SQLAlchemy ORM aapko Python mein easily database ko manage karne ka tareeqa deta hai.
# Session ek temporary connection hai jo aapko database se interact karne, data ko add/update/delete karne mein madad karta hai.
from schems import UserCreate, PatientCreate, MedicalHistoryBase
from table import User, Patient, MedicalHistory, ChatHistory
from database import get_db

#Api chatbot kidr hie Apiiiii
router = APIRouter(prefix="/user", tags=["user"]) # tag ko hum s lia lgaty hain taky swager ui mn apis ka easyli pta chl jy 

@router.post("/register")
def register_user(create_user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(username=create_user.username, email=create_user.email, password=create_user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created successfully", "user": db_user}
    except Exception as e:
        db.rollback()  # Agar sab kuch theek chale to db.commit() se changes save ho jate hain.
# Agar koi error aaye to db.rollback() se sab changes wapas ho jate hain aur database clean ho jata hai.
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

# Route to create a new patient record
@router.post("/patients")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        # Create a new Patient instance and add it to the database
        db_patient = Patient(
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            address=patient.address
        )
        db.add(db_patient)
        db.commit()  # Commit the transaction
        db.refresh(db_patient)  # Refresh to get the latest data
        
        return {"message": "Patient created successfully", "patient": db_patient}
    except Exception as e:
        
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.post("/{patient_id}")
def create_medical_history(patient_id: int, medical_history: MedicalHistoryBase, db: Session = Depends(get_db)):
    try:
        # Pehle hum yeh check karte hain ke patient exist karta hai ya nahi
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        # Agar patient nahi milta, toh 404 error raise karte hain
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Agar patient mil gaya, toh hum ek naya MedicalHistory record create karte hain aur usse patient ke saath link karte hain
        db_medical_history = MedicalHistory(
            diagnosis=medical_history.diagnosis,  # Patient ka diagnosis
            treatment=medical_history.treatment,  # Patient ka treatment
            allergies=medical_history.allergies,  # Patient ki allergies
            patient_id=patient_id  # Yeh ID patient ke saath associate karti hai
        )
        
        # Naye medical history record ko database mein add karte hain
        db.add(db_medical_history)
        
        # Transaction ko commit karte hain, taake data save ho jaye
        db.commit()  
        
        # Newly added record ko refresh karte hain taake updated data mil sake
        db.refresh(db_medical_history)  
        
        # Success message aur newly added medical history return karte hain
        return {"message": "Medical history added successfully", "medical_history": db_medical_history}
    
    except Exception as e:
        # Agar koi error hoti hai, toh 500 error ke saath message bhejte hain
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Route to fetch a patient's medical history
@router.get("/{patient_id}")
def medical_history(patient_id: int, db: Session = Depends(get_db)):
    # Query the Patient table to get the patient by ID
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if patient is None:
        # If the patient does not exist, raise an HTTP exception
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Return patient name and medical history
    return {"patient": patient.name, "medical_history": patient.medical_histories}

# Route to get all patients' medical histories (if needed)
@router.get("/")
def patient_medical_history(db: Session = Depends(get_db)):
    # Fetch all patients and their medical histories
    patients = db.query(Patient).all()
    result = []
    for patient in patients:
        result.append({
            "patient_name": patient.name,
            "medical_histories": patient.medical_histories
        })
    return {"patients_medical_history": result}

@router.get("/chats/user/{user_id}")
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    """Return chat history for a user ordered by newest first."""
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc()).all()
    return {
        "chats": [
            {
                "id": c.id,
                "user_input": c.user_input,
                "ai_response": c.ai_response,
                "created_at": c.created_at,
                "patient_id": c.patient_id,
                "user_id": c.user_id,
            }
            for c in chats
        ]
    }

@router.get("/chats/patient/{patient_id}")
def get_patient_chats(patient_id: int, db: Session = Depends(get_db)):
    """Return chat history for a patient ordered by newest first."""
    chats = db.query(ChatHistory).filter(ChatHistory.patient_id == patient_id).order_by(ChatHistory.created_at.desc()).all()
    return {
        "chats": [
            {
                "id": c.id,
                "user_input": c.user_input,
                "ai_response": c.ai_response,
                "created_at": c.created_at,
                "patient_id": c.patient_id,
                "user_id": c.user_id,
            }
            for c in chats
        ]
    }




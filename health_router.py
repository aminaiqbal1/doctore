from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth, ai_agent  # Changed from ... to ..

router = APIRouter(prefix="/health", tags=["health"])

@router.post("/consult", response_model=schemas.ConsultationResponse)
async def create_consultation(
    consultation: schemas.ConsultationCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Run the AI health assistant
    initial_state = {
        "problem": consultation.problem_description,
        "analysis": "",
        "recommendations": "",
        "exercises": "",
        "disclaimer": ""
    }
    
    result = ai_agent.health_assistant.invoke(initial_state)
    
    # Combine AI responses
    ai_response = f"""
    **Analysis:**
    {result['analysis']}
    
    **Recommendations:**
    {result['recommendations']}
    
    **Exercises:**
    {result['exercises']}
    
    {result['disclaimer']}
    """
    
    # Save consultation
    db_consultation = models.Consultation(
        user_id=current_user.id,
        problem_description=consultation.problem_description,
        ai_recommendation=ai_response
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    
    return db_consultation

@router.get("/consultations", response_model=List[schemas.ConsultationResponse])
def get_consultations(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return db.query(models.Consultation).filter(
        models.Consultation.user_id == current_user.id
    ).order_by(models.Consultation.created_at.desc()).all()
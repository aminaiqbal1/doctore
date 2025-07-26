from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth, ai_agent  # Changed from ... to ..

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/entry", response_model=schemas.ProgressEntryResponse)
async def create_progress_entry(
    entry: schemas.ProgressEntryCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Verify consultation belongs to user
    consultation = db.query(models.Consultation).filter(
        models.Consultation.id == entry.consultation_id,
        models.Consultation.user_id == current_user.id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    # Get previous progress entries
    previous_entries = db.query(models.ProgressEntry).filter(
        models.ProgressEntry.user_id == current_user.id,
        models.ProgressEntry.consultation_id == entry.consultation_id
    ).order_by(models.ProgressEntry.date.desc()).limit(5).all()
    
    # Get AI feedback
    ai_feedback = ai_agent.analyze_progress(
        [{"date": p.date, "mood": p.mood_rating, "symptoms": p.symptoms_improved} 
         for p in previous_entries],
        {
            "description": entry.description,
            "mood_rating": entry.mood_rating,
            "symptoms_improved": entry.symptoms_improved
        }
    )
    
    # Save progress entry
    db_progress = models.ProgressEntry(
        user_id=current_user.id,
        consultation_id=entry.consultation_id,
        description=entry.description,
        mood_rating=entry.mood_rating,
        symptoms_improved=entry.symptoms_improved,
        ai_feedback=ai_feedback
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    
    return db_progress

@router.get("/entries/{consultation_id}", response_model=List[schemas.ProgressEntryResponse])
def get_progress_entries(
    consultation_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Verify consultation belongs to user
    consultation = db.query(models.Consultation).filter(
        models.Consultation.id == consultation_id,
        models.Consultation.user_id == current_user.id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    return db.query(models.ProgressEntry).filter(
        models.ProgressEntry.consultation_id == consultation_id
    ).order_by(models.ProgressEntry.date.desc()).all()

@router.get("/summary")
def get_progress_summary(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Get all progress entries for the user
    entries = db.query(models.ProgressEntry).filter(
        models.ProgressEntry.user_id == current_user.id
    ).order_by(models.ProgressEntry.date.desc()).all()
    
    if not entries:
        return {"message": "No progress entries found"}
    
    # Calculate average mood over time
    mood_data = [{"date": e.date, "mood": e.mood_rating} for e in entries]
    avg_mood = sum(e.mood_rating for e in entries) / len(entries)
    
    return {
        "total_entries": len(entries),
        "average_mood": round(avg_mood, 2),
        "mood_trend": mood_data[:10],  # Last 10 entries
        "latest_entry": entries[0] if entries else None
    }
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.database.repositories.cv_repo import CVRepository
from app.intelligence.cv_parser import CVParser
from app.schemas.cv import CVProfileRead, CVProfileUpdate

router = APIRouter(prefix="/cv", tags=["cv"])

@router.post("/upload", response_model=CVProfileRead)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingests and parses a CV document (PDF, DOCX, TXT).
    Extracts structured technical profile, project evidence, and seniority level.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pdf", "docx", "txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats are PDF, DOCX, and TXT.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size exceeds maximum 10MB limit.")

    parser = CVParser()
    try:
        parsed_data = parser.parse(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Document parsing error: {str(e)}")

    repo = CVRepository(db)
    profile = repo.save_profile(parsed_data)
    return CVProfileRead.model_validate(profile)


@router.get("/profile", response_model=Optional[CVProfileRead])
def get_active_profile(db: Session = Depends(get_db)):
    """
    Retrieves the active CV profile (approved or most recently uploaded).
    """
    repo = CVRepository(db)
    profile = repo.get_active_profile()
    if not profile:
        return None
    return CVProfileRead.model_validate(profile)


@router.put("/profile/{profile_id}", response_model=CVProfileRead)
def update_profile(
    profile_id: str,
    updates: CVProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates the extracted profile fields and enables user approval.
    """
    repo = CVRepository(db)
    updated = repo.update_profile(profile_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="CV profile not found")
    return CVProfileRead.model_validate(updated)


@router.post("/profile/{profile_id}/approve", response_model=CVProfileRead)
def approve_profile(
    profile_id: str,
    db: Session = Depends(get_db),
):
    """
    Approves the profile for active opportunity matching.
    """
    repo = CVRepository(db)
    updated = repo.update_profile(profile_id, {"approved": True})
    if not updated:
        raise HTTPException(status_code=404, detail="CV profile not found")
    return CVProfileRead.model_validate(updated)


@router.delete("", response_model=dict)
def delete_all_cv_data(db: Session = Depends(get_db)):
    """
    Securely deletes all stored CV data and extracted profiles.
    """
    repo = CVRepository(db)
    count = repo.delete_all()
    return {"status": "success", "deleted_profiles": count}

"""Interaction CRUD API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.interaction import Interaction
from app.models.hcp import HCP
from app.schemas.interaction import InteractionCreate, InteractionUpdate, InteractionResponse

router = APIRouter()


@router.get("/interactions", response_model=List[InteractionResponse])
def list_interactions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all interactions, ordered by most recent first."""
    interactions = (
        db.query(Interaction)
        .order_by(Interaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [InteractionResponse(**i.to_dict()) for i in interactions]


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a single interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return InteractionResponse(**interaction.to_dict())


@router.post("/interactions", response_model=InteractionResponse)
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Manually create an interaction (fallback if AI is bypassed)."""
    interaction = Interaction(**data.model_dump(exclude_none=True))
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return InteractionResponse(**interaction.to_dict())


@router.put("/interactions/{interaction_id}", response_model=InteractionResponse)
def update_interaction(interaction_id: int, data: InteractionUpdate, db: Session = Depends(get_db)):
    """Update an interaction."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return InteractionResponse(**interaction.to_dict())


@router.delete("/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Delete an interaction."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    db.delete(interaction)
    db.commit()
    return {"message": f"Interaction {interaction_id} deleted"}


@router.get("/hcps")
def list_hcps(db: Session = Depends(get_db)):
    """List all HCPs."""
    hcps = db.query(HCP).all()
    return [
        {
            "id": h.id,
            "name": h.name,
            "specialization": h.specialization,
            "hospital": h.hospital,
            "city": h.city,
        }
        for h in hcps
    ]

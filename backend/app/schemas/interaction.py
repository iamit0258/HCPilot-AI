from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InteractionBase(BaseModel):
    """Base interaction fields."""
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    meeting_date: Optional[str] = None
    meeting_time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    products_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    summary: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None


class InteractionCreate(InteractionBase):
    """Schema for creating a new interaction."""
    pass


class InteractionUpdate(InteractionBase):
    """Schema for updating an interaction — all fields optional (PATCH semantics)."""
    pass


class InteractionResponse(InteractionBase):
    """Schema for interaction API responses."""
    id: int
    hcp_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

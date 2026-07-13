from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Interaction(Base):
    """HCP Interaction model — records a meeting/interaction with a doctor."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=True)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(100), nullable=True)  # In-Person, Virtual, Phone, Email
    meeting_date = Column(String(50), nullable=True)
    meeting_time = Column(String(50), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    products_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # Positive, Neutral, Negative
    summary = Column(Text, nullable=True)
    follow_up_date = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")

    def to_dict(self):
        """Convert interaction to dictionary for API responses."""
        return {
            "id": self.id,
            "hcp_id": self.hcp_id,
            "hcp_name": self.hcp_name,
            "interaction_type": self.interaction_type,
            "meeting_date": self.meeting_date,
            "meeting_time": self.meeting_time,
            "attendees": self.attendees,
            "topics_discussed": self.topics_discussed,
            "products_discussed": self.products_discussed,
            "materials_shared": self.materials_shared,
            "samples_distributed": self.samples_distributed,
            "sentiment": self.sentiment,
            "summary": self.summary,
            "follow_up_date": self.follow_up_date,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Interaction(id={self.id}, hcp='{self.hcp_name}', date='{self.meeting_date}')>"

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class HCP(Base):
    """Healthcare Professional model."""
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp")

    def __repr__(self):
        return f"<HCP(id={self.id}, name='{self.name}')>"

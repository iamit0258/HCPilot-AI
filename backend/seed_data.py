"""Seed the database with sample HCPs and products for demo purposes."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models.hcp import HCP
from app.models.interaction import Interaction


SAMPLE_HCPS = [
    {
        "name": "Dr. Sharma",
        "specialization": "Cardiology",
        "hospital": "Apollo Hospital",
        "city": "Mumbai",
        "email": "sharma@apollo.com",
        "phone": "+91-9876543210",
    },
    {
        "name": "Dr. Smith",
        "specialization": "Neurology",
        "hospital": "City Medical Center",
        "city": "Delhi",
        "email": "smith@citymed.com",
        "phone": "+91-9876543211",
    },
    {
        "name": "Dr. John",
        "specialization": "Oncology",
        "hospital": "Max Healthcare",
        "city": "Bangalore",
        "email": "john@maxhealth.com",
        "phone": "+91-9876543212",
    },
    {
        "name": "Dr. Patel",
        "specialization": "Endocrinology",
        "hospital": "Fortis Hospital",
        "city": "Ahmedabad",
        "email": "patel@fortis.com",
        "phone": "+91-9876543213",
    },
    {
        "name": "Dr. Williams",
        "specialization": "Pulmonology",
        "hospital": "AIIMS",
        "city": "Delhi",
        "email": "williams@aiims.com",
        "phone": "+91-9876543214",
    },
]


def seed_database():
    """Populate the database with sample data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(HCP).count()
        if existing > 0:
            print(f"Database already has {existing} HCPs. Skipping seed.")
            return

        # Insert HCPs
        for hcp_data in SAMPLE_HCPS:
            hcp = HCP(**hcp_data)
            db.add(hcp)

        db.commit()
        print(f"Seeded {len(SAMPLE_HCPS)} HCPs successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

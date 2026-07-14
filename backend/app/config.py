import os
from dotenv import load_dotenv

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcpilot.db")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

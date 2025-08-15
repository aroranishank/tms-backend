import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskmanager.db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
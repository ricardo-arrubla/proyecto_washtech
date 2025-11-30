import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'washtech-secret-key-2025'
    # Prioriza DATABASE_URL (usado por Railway en producción)
    # Fallback: PostgreSQL local para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:pupiales8@localhost:5432/washtech_local'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
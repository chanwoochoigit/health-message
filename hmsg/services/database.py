"""Database models and configuration for the health message application."""

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import os
from datetime import datetime

# Database configuration with PostgreSQL default
# Use system username for macOS Homebrew PostgreSQL installations
import getpass
default_user = getpass.getuser()
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql://{default_user}@localhost:5432/health_message_db"  # PostgreSQL default
)

try:
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Test connection
    with engine.connect() as conn:
        pass
    print(f"✅ Database connected: {DATABASE_URL.split('://')[0]}")
    
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    print("Please ensure PostgreSQL is running and database exists.")


class ProfileType(enum.Enum):
    """User profile types."""
    DOC = "doc"
    PATIENT = "patient"


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    profile = Column(Enum(ProfileType), nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    """Extended patient information."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)  # Primary identifier for patients
    user_id = Column(Integer, sa.ForeignKey("users.id"), nullable=True)  # Optional link to User
    age = Column(Integer)
    target_achieved = Column(sa.Boolean, default=False)
    last_heart_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PatientRecords(Base):
    """Patient exercise and health records table."""
    __tablename__ = "patient_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, sa.ForeignKey("patients.id"), nullable=False)  # Link to Patient table
    username = Column(String, nullable=False)  # Reference key to match patients
    
    # Date and session info
    date = Column(Date, nullable=False)
    week_number = Column(Integer)
    week_description = Column(String)  # e.g., "Week 1 (190.7 mins)"
    
    # Heart rate measurements
    hr_fat_burn = Column(Float)  # HR (fat burn)
    hr_mvpa = Column(Float)      # HR MVPA 
    hr_intense = Column(Float)   # HR (intense)
    
    # Duration tracking
    total_mins_per_session = Column(Float)  # Total mins (per session)
    total_weekly = Column(Float)            # Total weekly
    
    # Program notes and boosts
    boost = Column(Text)  # Boost notes (e.g., "Intro week", "Boost not delivered")
    notes = Column(Text)  # Additional notes
    
    # File uploads
    report_file_path = Column(String)  # Path to uploaded report file
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False 
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    candidates = relationship("Candidate", back_populates="owner")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    job_description = Column(Text)
    status = Column(String, default="Saved")
    
    # Scores
    match_score = Column(Float)
    skill_score = Column(Float)
    experience_score = Column(Float)
    education_score = Column(Float)
    ats_score = Column(Float)
    
    # Lists stored as comma-separated strings or JSON strings
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="candidates")

    created_at = Column(DateTime, default=datetime.utcnow)

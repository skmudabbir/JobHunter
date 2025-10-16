from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str
    description: str
    url: str
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    file_path: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    company: str
    position: str
    notes: str

class JobPosting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    published_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

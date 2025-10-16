from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import SQLModel, Session, create_engine, select, text  # ADD text import
from backend.database import get_db, create_db_and_tables
from backend.models import Application, Resume
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
import httpx
import feedparser
import asyncio
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(title="JobHunter", version="1.0.0")

# Mount static files and templates - FIXED PATH
app.mount("/static", StaticFiles(directory="/app/backend/static"), name="static")  # Use backend/static
templates = Jinja2Templates(directory="frontend/templates")

# Database setup - use environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")
# Replace postgres:// with postgresql:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL for Render PostgreSQL
if "render.com" in DATABASE_URL and "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ... (keep your existing dashboard and applications routes) ...

@app.get("/resumes")
async def resume_manager(request: Request, db: Session = Depends(get_db)):
    # Get resumes from database AND file system
    db_resumes = db.exec(select(Resume)).all()
    
    # Get file system resumes
    file_resumes = []
    if os.path.exists(RESUMES_DIR):
        for filename in os.listdir(RESUMES_DIR):
            if filename.endswith(('.pdf', '.doc', '.docx')):
                file_path = os.path.join(RESUMES_DIR, filename)
                file_resumes.append({
                    "filename": filename,
                    "upload_time": datetime.fromtimestamp(os.path.getctime(file_path)),
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path)
                })
    
    return templates.TemplateResponse("resumes.html", {
        "request": request, 
        "db_resumes": db_resumes,
        "file_resumes": file_resumes
    })

# Ensure resumes directory exists
RESUMES_DIR = "resumes"
os.makedirs(RESUMES_DIR, exist_ok=True)

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    db: Session = Depends(get_db)  # ADD database session
):
    try:
        # Validate file type
        allowed_extensions = ('.pdf', '.doc', '.docx')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(400, "Only PDF, DOC, and DOCX files allowed")
        
        # Validate file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(400, "File too large. Maximum size is 10MB")
        
        # Create safe filename
        safe_filename = f"{candidate_email}_{file.filename}".replace(" ", "_")
        file_location = os.path.join(RESUMES_DIR, safe_filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Save to database
        resume = Resume(
            filename=safe_filename,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            file_path=file_location,
            file_size=file_size,
            upload_date=datetime.now()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return JSONResponse({
            "status": "success",
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "saved_as": safe_filename,
            "resume_id": resume.id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.get("/api/resumes")
async def list_resumes(db: Session = Depends(get_db)):
    try:
        # Get from database
        db_resumes = db.exec(select(Resume)).all()
        
        # Get from file system as backup
        file_resumes = []
        if os.path.exists(RESUMES_DIR):
            for filename in os.listdir(RESUMES_DIR):
                if filename.endswith(('.pdf', '.doc', '.docx')):
                    file_path = os.path.join(RESUMES_DIR, filename)
                    file_resumes.append({
                        "filename": filename,
                        "upload_time": os.path.getctime(file_path),
                        "file_path": file_path
                    })
        
        return {
            "db_resumes": [{
                "id": r.id,
                "filename": r.filename,
                "candidate_name": r.candidate_name,
                "candidate_email": r.candidate_email,
                "upload_date": r.upload_date.isoformat() if r.upload_date else None
            } for r in db_resumes],
            "file_resumes": file_resumes
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to list resumes: {str(e)}")

@app.get("/api/download-resume/{resume_id}")
async def download_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(404, "Resume not found")
    
    return FileResponse(
        resume.file_path,
        filename=resume.filename,
        media_type='application/octet-stream'
    )

# ... (keep your existing optimize_resume, jobs/rss, and scrape routes) ...

# FIXED debug database endpoint
@app.get("/debug/database")
async def debug_database():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {
                "status": "error", 
                "message": "DATABASE_URL environment variable not set"
            }
        
        # Test connection with proper text() wrapper
        engine = create_engine(database_url)
        with Session(engine) as session:
            # Test 1: Basic connection
            result = session.exec(text("SELECT 1 as test"))
            basic_test = result.first()
            
            # Test 2: Check if tables exist
            if "sqlite" in database_url:
                table_check = session.exec(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """))
            else:  # PostgreSQL
                table_check = session.exec(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
            
            tables = [row[0] for row in table_check]
            
        return {
            "status": "success", 
            "message": "Database connection successful",
            "basic_test": basic_test,
            "existing_tables": tables,
            "database_type": "SQLite" if "sqlite" in database_url else "PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Database connection failed",
            "error": str(e)
        }

@app.get("/debug/resumes")
async def debug_resumes():
    """Debug endpoint to check resume directory and files"""
    resumes_dir_exists = os.path.exists(RESUMES_DIR)
    files = []
    
    if resumes_dir_exists:
        files = os.listdir(RESUMES_DIR)
    
    return {
        "resumes_dir_exists": resumes_dir_exists,
        "resumes_dir_path": os.path.abspath(RESUMES_DIR),
        "files_in_resumes_dir": files,
        "current_working_dir": os.getcwd()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "JobHunter API is running"}

# Add CORS if needed (for mobile app)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
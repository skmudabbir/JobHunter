from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import SQLModel, Session, create_engine, select, text
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

# Debug current directory structure
print("Current working directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))
if os.path.exists('backend'):
    print("Backend contents:", os.listdir('backend'))
if os.path.exists('frontend'):
    print("Frontend contents:", os.listdir('frontend'))

# Mount static files and templates with fallbacks
try:
    app.mount("/static", StaticFiles(directory="/app/backend/static"), name="static")
    print("Mounted static files at /app/backend/static")
except Exception as e:
    print(f"Static files error: {e}")
    try:
        app.mount("/static", StaticFiles(directory="backend/static"), name="static")
        print("Mounted static files at backend/static")
    except Exception as e2:
        print(f"Backup static files error: {e2}")

try:
    templates = Jinja2Templates(directory="frontend/templates")
    print("Templates loaded from frontend/templates")
except Exception as e:
    print(f"Templates error: {e}")

# Database setup with better error handling
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")
print(f"Database URL: {DATABASE_URL[:50]}...")  # Log first 50 chars

# Replace postgres:// with postgresql:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL for Render PostgreSQL
if "render.com" in DATABASE_URL and "?" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    print("Database engine created successfully")
except Exception as e:
    print(f"Database engine creation failed: {e}")
    # Fallback to SQLite
    DATABASE_URL = "sqlite:///./jobhunter.db"
    engine = create_engine(DATABASE_URL)
    print("Using SQLite fallback")

@app.on_event("startup")
def on_startup():
    try:
        create_db_and_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database table creation failed: {e}")

# Basic routes that should always work
# @app.get("/")
# async def root():
#     return {"message": "JobHunter API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "JobHunter API is running"}

# Debug endpoints
@app.get("/debug")
async def debug_info():
    return {
        "current_directory": os.getcwd(),
        "directory_contents": os.listdir('.'),
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "static_files_path": "/app/backend/static",
        "templates_path": "frontend/templates"
    }

@app.get("/debug/database")
async def debug_database():
    try:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")
        
        # Test connection
        engine = create_engine(database_url)
        with Session(engine) as session:
            # Test basic connection
            result = session.exec(text("SELECT 1 as test"))
            basic_test = result.first()
            
            # Convert Row to dict for JSON serialization
            basic_test_dict = dict(basic_test._mapping) if basic_test else {"test": None}
            
            # Check if tables exist
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
            "basic_test": basic_test_dict,
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
    RESUMES_DIR = "resumes"
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

# Template routes with error handling
@app.get("/")
async def dashboard(request: Request):
    try:
        db = next(get_db())
        applications = db.exec(select(Application)).all()
        return templates.TemplateResponse("dashboard.html", {"request": request, "applications": applications})
    except Exception as e:
        return JSONResponse({"error": f"Dashboard failed: {str(e)}"}, status_code=500)

# Template routes with error handling
@app.get("/dashboard")
async def dashboard(request: Request):
    try:
        db = next(get_db())
        applications = db.exec(select(Application)).all()
        return templates.TemplateResponse("dashboard.html", {"request": request, "applications": applications})
    except Exception as e:
        return JSONResponse({"error": f"Dashboard failed: {str(e)}"}, status_code=500)


@app.get("/jobs/scrape")
async def scrape_jobs(request: Request):
    try:
        return templates.TemplateResponse("scraper.html", {"request": request})
    except Exception as e:
        return JSONResponse({"error": f"Template not found: {str(e)}"}, status_code=500)

@app.get("/resumes")
async def resume_manager(request: Request):
    try:
        db = next(get_db())
        db_resumes = db.exec(select(Resume)).all()
        
        # Get file system resumes
        file_resumes = []
        RESUMES_DIR = "resumes"
        if os.path.exists(RESUMES_DIR):
            for filename in os.listdir(RESUMES_DIR):
                if filename.endswith(('.pdf', '.doc', '.docx')):
                    file_path = os.path.join(RESUMES_DIR, filename)
                    file_resumes.append({
                        "filename": filename,
                        "upload_time": datetime.fromtimestamp(os.path.getctime(file_path)),
                        "file_path": file_path,
                    })
        
        return templates.TemplateResponse("resumes.html", {
            "request": request, 
            "db_resumes": db_resumes,
            "file_resumes": file_resumes
        })
    except Exception as e:
        return JSONResponse({"error": f"Resumes page failed: {str(e)}"}, status_code=500)
# Add missing routes
@app.get("/applications-page")
async def applications_page(request: Request):
    try:
        db = next(get_db())
        applications = db.exec(select(Application)).all()
        return templates.TemplateResponse("applications.html", {"request": request, "applications": applications})
    except Exception as e:
        return JSONResponse({"error": f"Applications page failed: {str(e)}"}, status_code=500)

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Form(...),
    candidate_email: str = Form(...)
):
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(400, "Only PDF, DOC, and DOCX files allowed")
        
        # Save file
        RESUMES_DIR = "resumes"
        os.makedirs(RESUMES_DIR, exist_ok=True)
        file_location = f"{RESUMES_DIR}/{candidate_email}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success",
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "saved_as": file_location
        }
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.get("/api/jobs/rss")
async def fetch_rss_jobs(url: str = None):
    try:
        # Default job RSS feeds
        default_feeds = [
            "https://stackoverflow.com/jobs/feed",
            "https://news.ycombinator.com/jobsrss"
        ]
        
        all_jobs = []
        
        async with httpx.AsyncClient() as client:
            for feed_url in default_feeds:
                try:
                    response = await client.get(feed_url, timeout=10.0)
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries[:5]:  # Limit to 5 per feed
                        job = {
                            "title": entry.title,
                            "link": entry.link,
                            "published": entry.published if hasattr(entry, 'published') else "",
                            "summary": entry.summary if hasattr(entry, 'summary') else "",
                            "source": feed_url
                        }
                        all_jobs.append(job)
                        
                except Exception as e:
                    print(f"Failed to fetch {feed_url}: {e}")
                    continue
        
        return {"jobs": all_jobs[:10]}  # Return max 10 jobs
        
    except Exception as e:
        raise HTTPException(500, f"RSS fetch failed: {str(e)}")

@app.post("/jobs/scrape")
async def start_scraping(request: Request):
    form_data = await request.form()
    feed_url = form_data.get("feed_url")
    keywords = form_data.get("keywords", "")
    
    # Mock scraping results
    jobs = [
        {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Looking for experienced Python developer with FastAPI knowledge.",
            "url": "https://example.com/jobs/1"
        },
        {
            "title": "Backend Engineer",
            "company": "Startup Inc",
            "location": "New York",
            "description": "Join our team to build scalable backend systems.",
            "url": "https://example.com/jobs/2"
        }
    ]
    
    jobs_html = "".join([f"""
    <div class="border border-gray-200 rounded-lg p-4 mb-3">
        <h4 class="font-semibold text-gray-800">{job['title']}</h4>
        <p class="text-gray-600 text-sm">{job['company']} • {job['location']}</p>
        <p class="text-gray-500 text-sm mt-2">{job['description'][:200]}...</p>
        <div class="flex justify-between items-center mt-3">
            <a href="{job['url']}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm">View Job</a>
            <button hx-post="/applications/create" 
                    hx-include="[name='job_id']" 
                    hx-target="#applications-table"
                    class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                Save & Apply
            </button>
            <input type="hidden" name="job_id" value="{job['title']}">
        </div>
    </div>
    """ for job in jobs])
    
    return HTMLResponse(f"""
    <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
        <p class="text-green-700">Found {len(jobs)} jobs from the RSS feed.</p>
    </div>
    <div class="space-y-3">
        {jobs_html}
    </div>
    """)
# Keep your existing API routes (upload-resume, jobs/rss, etc.)
# ... [your existing API routes here] ...

# Add CORS if needed
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
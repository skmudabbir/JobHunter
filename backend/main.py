from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine, select
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

load_dotenv()

app = FastAPI(title="JobHunter", version="1.0.0")

# Mount static files and templates
#app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/static", StaticFiles(directory="/app/frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Database setup - use environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")
# Replace postgres:// with postgresql:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    applications = db.exec(select(Application)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "applications": applications})

@app.get("/applications")
async def list_applications(request: Request, status: str = None, db: Session = Depends(get_db)):
    query = select(Application)
    if status:
        query = query.where(Application.status == status)
    applications = db.exec(query).all()
    return templates.TemplateResponse("applications/partial.html", {"request": request, "applications": applications})

@app.get("/applications-page")
async def applications_page(request: Request, db: Session = Depends(get_db)):
    applications = db.exec(select(Application)).all()
    return templates.TemplateResponse("applications.html", {"request": request, "applications": applications})

@app.post("/applications/create")
async def create_application(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    job_id = form_data.get("job_id", "manual")
    
    application = Application(
        title=f"Job {job_id}",
        company="Example Company",
        location="Remote",
        description="Job description here",
        url=f"http://example.com/jobs/{job_id}",
        status="applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Return updated applications list
    applications = db.exec(select(Application)).all()
    return templates.TemplateResponse("applications/partial.html", {"request": request, "applications": applications})

@app.get("/resumes")
async def resume_manager(request: Request, db: Session = Depends(get_db)):
    resumes = db.exec(select(Resume)).all()
    return templates.TemplateResponse("resumes.html", {"request": request, "resumes": resumes})
# Ensure resumes directory exists
RESUMES_DIR = "resumes"
os.makedirs(RESUMES_DIR, exist_ok=True)

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

@app.get("/api/resumes")
async def list_resumes():
    try:
        resumes = []
        if os.path.exists(RESUMES_DIR):
            for filename in os.listdir(RESUMES_DIR):
                if filename.endswith(('.pdf', '.doc', '.docx')):
                    resumes.append({
                        "filename": filename,
                        "upload_time": os.path.getctime(f"{RESUMES_DIR}/{filename}")
                    })
        return {"resumes": resumes}
    except Exception as e:
        raise HTTPException(500, f"Failed to list resumes: {str(e)}")
@app.post("/resumes/optimize")
async def optimize_resume(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    resume_id = form_data.get("resume_id")
    job_description = form_data.get("job_description")
    
    # Mock optimization result
    result = {
        "method": "basic",
        "match_score": 75,
        "included_keywords": ["python", "fastapi", "sql"],
        "missing_keywords": ["docker", "aws", "react"],
        "suggestions": "Add Docker and AWS experience to improve match"
    }
    
    return HTMLResponse(f"""
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 class="font-semibold text-blue-800 mb-2">Optimization Results</h4>
        <p class="text-blue-700"><strong>Match Score:</strong> {result['match_score']}%</p>
        <p class="text-blue-700"><strong>Missing Keywords:</strong> {', '.join(result['missing_keywords'])}</p>
        <p class="text-blue-700"><strong>Suggestions:</strong> {result['suggestions']}</p>
    </div>
    """)
@app.get("/api/jobs/rss")
async def fetch_rss_jobs(url: str = None):
    try:
        # Default job RSS feeds if no URL provided
        default_feeds = [
            "https://stackoverflow.com/jobs/feed",
            "https://www.indeed.com/rss?q=python&l=remote",
            "https://news.ycombinator.com/jobsrss"
        ]
        
        all_jobs = []
        
        async with httpx.AsyncClient() as client:
            for feed_url in default_feeds:
                try:
                    response = await client.get(feed_url, timeout=10.0)
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries[:10]:  # Limit to 10 per feed
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
        
        return {"jobs": all_jobs[:20]}  # Return max 20 jobs
        
    except Exception as e:
        raise HTTPException(500, f"RSS fetch failed: {str(e)}")
@app.get("/jobs/scrape")
async def scrape_jobs(request: Request):
    return templates.TemplateResponse("scraper.html", {"request": request})

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
# Add database debug endpoint
@app.get("/debug/database")
async def debug_database():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {"status": "error", "message": "DATABASE_URL not set"}
        
        engine = create_engine(database_url)
        with Session(engine) as session:
            # Test simple query
            session.exec("SELECT 1")
            
        return {
            "status": "success", 
            "message": "Database connection successful",
            "database_url": database_url[:20] + "..." if database_url else "Not set"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

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

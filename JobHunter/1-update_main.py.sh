# Update backend/main.py to include the missing routes
cat > backend/main.py << 'EOF'
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from backend.database import get_db, create_db_and_tables
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="JobHunter", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobhunter.db")
engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    from backend.models import Application
    applications = db.exec(select(Application)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "applications": applications})

@app.get("/applications")
async def list_applications(request: Request, status: str = None, db: Session = Depends(get_db)):
    from backend.models import Application
    query = select(Application)
    if status:
        query = query.where(Application.status == status)
    applications = db.exec(query).all()
    return templates.TemplateResponse("applications/partial.html", {"request": request, "applications": applications})

@app.get("/applications-page")
async def applications_page(request: Request, db: Session = Depends(get_db)):
    from backend.models import Application
    applications = db.exec(select(Application)).all()
    return templates.TemplateResponse("applications.html", {"request": request, "applications": applications})

@app.post("/applications/create")
async def create_application(job_id: str, db: Session = Depends(get_db)):
    # Implementation for creating application
    from backend.models import Application
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
    from fastapi.responses import HTMLResponse
    from backend.main import templates
    return HTMLResponse(content=templates.get_template("applications/partial.html").render(request=Request, applications=applications))

@app.get("/resumes")
async def resume_manager(request: Request, db: Session = Depends(get_db)):
    from backend.models import Resume
    resumes = db.exec(select(Resume)).all()
    return templates.TemplateResponse("resumes.html", {"request": request, "resumes": resumes})

@app.post("/resumes/optimize")
async def optimize_resume(resume_id: str, job_description: str, db: Session = Depends(get_db)):
    from backend.services.resume_optimizer import optimize_resume
    # For now, return a mock result
    result = {
        "method": "basic",
        "match_score": 75,
        "included_keywords": ["python", "fastapi", "sql"],
        "missing_keywords": ["docker", "aws", "react"],
        "suggestions": "Add Docker and AWS experience to improve match"
    }
    from fastapi.responses import HTMLResponse
    return HTMLResponse(f"""
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 class="font-semibold text-blue-800 mb-2">Optimization Results</h4>
        <p class="text-blue-700"><strong>Match Score:</strong> {result['match_score']}%</p>
        <p class="text-blue-700"><strong>Missing Keywords:</strong> {', '.join(result['missing_keywords'])}</p>
        <p class="text-blue-700"><strong>Suggestions:</strong> {result['suggestions']}</p>
    </div>
    """)

@app.get("/jobs/scrape")
async def scrape_jobs(request: Request):
    return templates.TemplateResponse("scraper.html", {"request": request})

@app.post("/jobs/scrape")
async def start_scraping(feed_url: str, keywords: str = ""):
    from backend.services.scraper import scrape_jobs_from_feed
    jobs = scrape_jobs_from_feed(feed_url, keywords)
    from fastapi.responses import HTMLResponse
    
    if jobs and "error" not in jobs[0]:
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
        """ for job in jobs[:5]])  # Show first 5 jobs
        
        return HTMLResponse(f"""
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <p class="text-green-700">Found {len(jobs)} jobs from the RSS feed.</p>
        </div>
        <div class="space-y-3">
            {jobs_html}
        </div>
        """)
    else:
        error_msg = jobs[0]['error'] if jobs else "No jobs found or scraping failed"
        return HTMLResponse(f"""
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-700">Scraping failed: {error_msg}</p>
        </div>
        """)

@app.get("/cover-letter/generate")
async def generate_cover_letter(application_id: str, db: Session = Depends(get_db)):
    from backend.services.cover_letter import generate_cover_letter
    letter = generate_cover_letter(application_id, db)
    return {"cover_letter": letter}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF
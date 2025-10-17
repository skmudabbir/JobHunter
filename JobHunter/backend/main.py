from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import SQLModel, Session, select
from backend.database import get_db, create_db_and_tables
from backend.models import Application, Resume, Contact, JobPosting, ApplicationStatus
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="JobHunter", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Create upload directory
os.makedirs("uploads/resumes", exist_ok=True)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Application startup completed")

@app.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        applications = db.exec(select(Application)).all()
        resumes = db.exec(select(Resume)).all()
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "applications": applications,
            "resumes": resumes
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "applications": [],
            "resumes": []
        })

# Applications endpoints
@app.get("/applications")
async def list_applications(request: Request, status: str = None, db: Session = Depends(get_db)):
    try:
        query = select(Application)
        if status:
            query = query.where(Application.status == status)
        applications = db.exec(query).all()
        return templates.TemplateResponse("applications/partial.html", {
            "request": request, 
            "applications": applications
        })
    except Exception as e:
        logger.error(f"List applications error: {e}")
        return HTMLResponse("<div class='text-red-500'>Error loading applications</div>")

@app.get("/applications-page")
async def applications_page(request: Request, db: Session = Depends(get_db)):
    try:
        applications = db.exec(select(Application)).all()
        return templates.TemplateResponse("applications.html", {
            "request": request, 
            "applications": applications
        })
    except Exception as e:
        logger.error(f"Applications page error: {e}")
        return templates.TemplateResponse("applications.html", {
            "request": request, 
            "applications": []
        })

@app.post("/applications/create")
async def create_application(
    request: Request,
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    status: str = Form("saved"),
    db: Session = Depends(get_db)
):
    try:
        application = Application(
            title=title,
            company=company,
            location=location,
            description=description,
            status=ApplicationStatus(status),
            applied_date=datetime.utcnow() if status == "applied" else None
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        
        applications = db.exec(select(Application)).all()
        return templates.TemplateResponse("applications/partial.html", {
            "request": request, 
            "applications": applications
        })
    except Exception as e:
        logger.error(f"Create application error: {e}")
        return HTMLResponse("<div class='text-red-500'>Error creating application</div>")

@app.post("/applications/{application_id}/delete")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    try:
        application = db.get(Application, application_id)
        if application:
            db.delete(application)
            db.commit()
        return JSONResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Delete application error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}")

# Resume endpoints
@app.get("/resumes")
async def resume_manager(request: Request, db: Session = Depends(get_db)):
    try:
        resumes = db.exec(select(Resume)).all()
        return templates.TemplateResponse("resumes.html", {
            "request": request, 
            "resumes": resumes
        })
    except Exception as e:
        logger.error(f"Resume manager error: {e}")
        return templates.TemplateResponse("resumes.html", {
            "request": request, 
            "resumes": []
        })

@app.post("/resumes/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Save file
        file_path = f"uploads/resumes/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create resume record
        resume = Resume(
            name=name,
            file_name=file.filename,
            file_path=file_path,
            content=f"Uploaded resume: {name}"  # In real app, extract text from file
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        resumes = db.exec(select(Resume)).all()
        return templates.TemplateResponse("resumes/partial.html", {
            "request": request, 
            "resumes": resumes
        })
    except Exception as e:
        logger.error(f"Upload resume error: {e}")
        return HTMLResponse("<div class='text-red-500'>Error uploading resume</div>")

@app.post("/resumes/{resume_id}/delete")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    try:
        resume = db.get(Resume, resume_id)
        if resume:
            # Delete file
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
            # Delete record
            db.delete(resume)
            db.commit()
        return JSONResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Delete resume error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}")

@app.post("/resumes/optimize")
async def optimize_resume(
    resume_id: int = Form(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        resume = db.get(Resume, resume_id)
        if not resume:
            return HTMLResponse("<div class='text-red-500'>Resume not found</div>")
        
        # Simple keyword matching (replace with actual NLP/OpenAI)
        keywords = ["python", "fastapi", "sql", "docker", "aws", "javascript", "react"]
        job_lower = job_description.lower()
        found_keywords = [kw for kw in keywords if kw in job_lower]
        missing_keywords = [kw for kw in keywords if kw not in job_lower]
        
        match_score = int((len(found_keywords) / len(keywords)) * 100)
        
        return HTMLResponse(f"""
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-semibold text-green-800 mb-2">Optimization Results</h4>
            <p class="text-green-700"><strong>Match Score:</strong> {match_score}%</p>
            <p class="text-green-700"><strong>Found Keywords:</strong> {', '.join(found_keywords)}</p>
            <p class="text-green-700"><strong>Missing Keywords:</strong> {', '.join(missing_keywords)}</p>
            <p class="text-green-700 mt-2"><strong>Suggestions:</strong> Add the missing keywords to your resume to improve match rate.</p>
        </div>
        """)
    except Exception as e:
        logger.error(f"Optimize resume error: {e}")
        return HTMLResponse(f"<div class='text-red-500'>Error optimizing resume: {str(e)}</div>")

# Job scraping endpoints
@app.get("/jobs/scrape")
async def scrape_jobs(request: Request):
    return templates.TemplateResponse("scraper.html", {"request": request})

@app.post("/jobs/scrape")
async def start_scraping(
    feed_url: str = Form(...),
    keywords: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        from backend.services.scraper import scrape_jobs_from_feed
        jobs = scrape_jobs_from_feed(feed_url, keywords)
        
        if jobs and "error" not in jobs[0]:
            # Save jobs to database
            for job_data in jobs:
                job = JobPosting(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    description=job_data["description"],
                    url=job_data["url"],
                    source=feed_url
                )
                db.add(job)
            db.commit()
            
            jobs_html = "".join([f"""
            <div class="border border-gray-200 rounded-lg p-4 mb-3">
                <h4 class="font-semibold text-gray-800">{job['title']}</h4>
                <p class="text-gray-600 text-sm">{job['company']} • {job['location']}</p>
                <p class="text-gray-500 text-sm mt-2">{job['description'][:200]}...</p>
                <div class="flex justify-between items-center mt-3">
                    <a href="{job['url']}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm">View Job</a>
                    <button hx-post="/applications/create" 
                            hx-include="[name='job_{idx}']" 
                            hx-target="#applications-table"
                            class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Save & Apply
                    </button>
                    <input type="hidden" name="title" value="{job['title']}">
                    <input type="hidden" name="company" value="{job['company']}">
                    <input type="hidden" name="location" value="{job['location']}">
                    <input type="hidden" name="description" value="{job['description']}">
                    <input type="hidden" name="status" value="saved">
                </div>
            </div>
            """ for idx, job in enumerate(jobs[:5])])
            
            return HTMLResponse(f"""
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <p class="text-green-700">Found {len(jobs)} jobs from the RSS feed and saved to database.</p>
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
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return HTMLResponse(f"<div class='text-red-500'>Scraping error: {str(e)}</div>")

# Health and debug endpoints
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.exec("SELECT 1")
        app_count = db.exec(select(Application)).all()
        resume_count = db.exec(select(Resume)).all()
        return {
            "status": "healthy", 
            "database": "connected",
            "applications": len(app_count),
            "resumes": len(resume_count)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    applications = db.exec(select(Application)).all()
    resumes = db.exec(select(Resume)).all()
    jobs = db.exec(select(JobPosting)).all()
    
    return {
        "applications": [{"id": app.id, "title": app.title, "company": app.company} for app in applications],
        "resumes": [{"id": res.id, "name": res.name, "file_name": res.file_name} for res in resumes],
        "job_postings": [{"id": job.id, "title": job.title, "company": job.company} for job in jobs]
    }

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

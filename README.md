# JobHunter - Full-Stack Job Search Assistant

JobHunter is a comprehensive job search application built with FastAPI (backend) and HTMX + TailwindCSS (frontend). It includes features for job scraping, application tracking, resume management, and AI-powered cover letter generation.

## 🚀 Features

- **Dashboard**: Overview of your job search progress
- **Job Scraper**: RSS feed-based job scraping with keyword filtering
- **Application Tracker**: Manage job applications with status tracking
- **Resume Manager**: Build, optimize, and manage multiple resumes
- **Cover Letter Generator**: AI-powered personalized cover letters
- **Mobile App**: Android WebView wrapper for mobile access
- **CI/CD**: Automated Android APK builds via GitHub Actions

## 🛠 Tech Stack

- **Backend**: FastAPI, SQLModel, SQLAlchemy
- **Frontend**: HTMX, TailwindCSS, Jinja2 Templates
- **Database**: SQLite (development), PostgreSQL (production)
- **AI/ML**: OpenAI GPT & local NLP (spaCy + YAKE) for resume optimization
- **Mobile**: Android Kotlin WebView
- **Deployment**: Docker, Render.com, GitHub Actions

## 📦 Quick Start

### Local Development

1. **Clone and setup**:
```bash
git clone <repository>
cd JobHunter
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

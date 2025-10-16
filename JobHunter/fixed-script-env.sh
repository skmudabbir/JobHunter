#!/bin/bash

# JobHunter Windows Setup Script (Fixed for Python 3.13)
echo "Setting up JobHunter on Windows..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Please activate virtual environment manually:"
    echo "  source venv/Scripts/activate"
    exit 1
fi

# Upgrade pip first
pip install --upgrade pip

# Install base requirements without problematic packages
echo "Installing base dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlmodel==0.0.14 python-dotenv==1.0.0
pip install python-multipart==0.0.6 jinja2==3.1.2 feedparser==6.0.10 python-docx==1.1.0
pip install reportlab==4.0.6 openai==1.3.0 alembic==1.12.1 psycopg2-binary==2.9.9 httpx==0.25.2

# Try installing spaCy with pre-compiled wheel, skip if it fails
echo "Attempting to install spaCy (may fail on Python 3.13)..."
pip install spacy==3.7.2 || echo "spaCy installation failed, continuing without it"

# Try installing YAKE, skip if it fails
pip install yake==0.4.9 || echo "YAKE installation failed, continuing without it"

# Initialize database
echo "Initializing database..."
python -c "
from backend.database import create_db_and_tables
from backend.models import *
create_db_and_tables()
print('Database initialized successfully!')
"

echo "✅ Setup complete!"
echo "🚀 To run the application:"
echo "   uvicorn backend.main:app --reload"
echo ""
echo "📝 Note: Some AI features may be limited if spaCy/YAKE failed to install"
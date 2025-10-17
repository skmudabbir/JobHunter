#!/bin/bash

echo "Setting up JobHunter..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "
from backend.database import create_db_and_tables
from backend.models import *
create_db_and_tables()
print('Database initialized successfully!')
"

echo "✅ Setup complete!"
echo "🚀 Run: uvicorn backend.main:app --reload"
echo "📱 App will be available at: http://localhost:8000"

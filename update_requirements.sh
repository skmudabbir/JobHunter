# Create production-ready requirements
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
python-dotenv==1.0.0
python-multipart==0.0.6
jinja2==3.1.2
feedparser==6.0.10
python-docx==1.1.0
reportlab==4.0.6
openai==1.3.0
alembic==1.12.1
psycopg2-binary==2.9.9
httpx==0.25.2
# Skip spaCy and YAKE for production to avoid build issues
EOF
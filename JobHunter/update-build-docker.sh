# Create docker build script
cat > build-docker.sh << 'EOF'
#!/bin/bash

echo "Building JobHunter Docker image..."

# Build the Docker image
docker build -t jobhunter .

echo "✅ Docker image built successfully!"
echo ""
echo "To run locally:"
echo "  docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./jobhunter.db jobhunter"
echo ""
echo "To test with PostgreSQL:"
echo "  docker run -p 8000:8000 -e DATABASE_URL=postgresql://user:pass@host/dbname jobhunter"
echo ""
echo "To push to Docker Hub:"
echo "  docker tag jobhunter yourusername/jobhunter:latest"
echo "  docker push yourusername/jobhunter:latest"
EOF

chmod +x build-docker.sh
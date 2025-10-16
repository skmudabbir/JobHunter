# JobHunter Deployment Guide

## Docker Deployment

### Build and test locally:
```bash
# Build the image
./build-docker.sh

# Test locally
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./jobhunter.db jobhunter

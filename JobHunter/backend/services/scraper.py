import feedparser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def scrape_jobs_from_feed(feed_url: str, keywords: str = "") -> list:
    """
    Scrape jobs from RSS/Atom feeds using feedparser
    """
    try:
        logger.info(f"Scraping from: {feed_url}")
        feed = feedparser.parse(feed_url)
        jobs = []
        
        # If it's a demo URL, return sample data
        if "example.com" in feed_url:
            return [
                {
                    "title": "Senior Python Developer",
                    "company": "Tech Solutions Inc",
                    "location": "Remote",
                    "description": "Looking for experienced Python developer with FastAPI and Django experience. Must have 5+ years of experience.",
                    "url": "https://example.com/jobs/101",
                    "source": feed_url
                },
                {
                    "title": "Full Stack Engineer",
                    "company": "Startup Ventures",
                    "location": "New York, NY",
                    "description": "Join our dynamic team building cutting-edge web applications with React and FastAPI.",
                    "url": "https://example.com/jobs/102",
                    "source": feed_url
                },
                {
                    "title": "DevOps Engineer",
                    "company": "Cloud Systems",
                    "location": "San Francisco, CA",
                    "description": "Manage our cloud infrastructure and CI/CD pipelines. Experience with AWS and Docker required.",
                    "url": "https://example.com/jobs/103",
                    "source": feed_url
                }
            ]
        
        for entry in feed.entries[:10]:  # Limit to 10 entries
            job = {
                "title": getattr(entry, 'title', 'No Title'),
                "company": getattr(entry, 'author', getattr(entry, 'company', 'Unknown Company')),
                "location": getattr(entry, 'location', 'Remote'),
                "description": getattr(entry, 'summary', getattr(entry, 'description', 'No description available')),
                "url": getattr(entry, 'link', '#'),
                "source": feed_url,
                "published_at": getattr(entry, 'published_parsed', datetime.utcnow())
            }
            
            # Filter by keywords if provided
            if keywords:
                keyword_list = [k.strip().lower() for k in keywords.split(',')]
                content = f"{job['title']} {job['description']}".lower()
                if any(keyword in content for keyword in keyword_list if keyword):
                    jobs.append(job)
            else:
                jobs.append(job)
                
        logger.info(f"Scraped {len(jobs)} jobs from {feed_url}")
        return jobs
    except Exception as e:
        logger.error(f"Scraping failed for {feed_url}: {e}")
        return [{"error": f"Scraping failed: {str(e)}"}]

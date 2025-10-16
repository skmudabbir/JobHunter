import feedparser
from datetime import datetime
from ..models import JobPosting

def scrape_jobs_from_feed(feed_url: str, keywords: str = "") -> list:
    """
    Scrape jobs from RSS/Atom feeds using feedparser
    """
    try:
        feed = feedparser.parse(feed_url)
        jobs = []
        
        for entry in feed.entries:
            job = {
                "title": entry.title,
                "company": getattr(entry, 'company', 'Unknown'),
                "location": getattr(entry, 'location', 'Remote'),
                "description": getattr(entry, 'summary', ''),
                "url": entry.link,
                "source": feed_url,
                "published_at": getattr(entry, 'published_parsed', datetime.utcnow())
            }
            
            # Filter by keywords if provided
            if keywords:
                keyword_list = [k.strip().lower() for k in keywords.split(',')]
                content = f"{job['title']} {job['description']}".lower()
                if any(keyword in content for keyword in keyword_list):
                    jobs.append(job)
            else:
                jobs.append(job)
                
        return jobs
    except Exception as e:
        return [{"error": f"Scraping failed: {str(e)}"}]

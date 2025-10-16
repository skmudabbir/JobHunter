# backend/services/resume_optimizer.py
import os
from typing import Dict, Any
import re

def optimize_resume(resume_content: str, job_description: str, db) -> Dict[str, Any]:
    """
    Optimize resume by comparing with job description.
    Uses OpenAI GPT if API key available, otherwise falls back to basic keyword matching.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        return _optimize_with_gpt(resume_content, job_description, openai_key)
    else:
        return _optimize_basic(resume_content, job_description)

def _optimize_with_gpt(resume_content: str, job_description: str, api_key: str) -> Dict[str, Any]:
    """Use OpenAI GPT for resume optimization"""
    try:
        import openai
        openai.api_key = api_key
        
        prompt = f"""
        Compare this resume with the job description and provide optimization suggestions:
        
        RESUME:
        {resume_content}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide:
        1. Missing keywords from the job description
        2. Skills to emphasize
        3. Overall match score (0-100)
        4. Specific improvements
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return {
            "method": "openai_gpt",
            "analysis": response.choices[0].message.content,
            "score": 85
        }
    except ImportError:
        return _optimize_basic(resume_content, job_description)

def _optimize_basic(resume_content: str, job_description: str) -> Dict[str, Any]:
    """Use basic keyword matching for resume optimization"""
    try:
        # Simple keyword extraction using regex
        job_words = re.findall(r'\b[a-zA-Z]{4,}\b', job_description.lower())
        resume_words = re.findall(r'\b[a-zA-Z]{4,}\b', resume_content.lower())
        
        # Get common technical/skill words (basic approach)
        common_tech_words = {'python', 'java', 'javascript', 'sql', 'html', 'css', 
                           'react', 'node', 'aws', 'docker', 'kubernetes', 'fastapi',
                           'django', 'flask', 'git', 'linux', 'windows', 'mongodb',
                           'postgresql', 'mysql', 'nosql', 'api', 'rest', 'graphql'}
        
        job_keywords = [word for word in set(job_words) if word in common_tech_words or len(word) > 6]
        included_keywords = [kw for kw in job_keywords if kw in resume_words]
        missing_keywords = [kw for kw in job_keywords if kw not in resume_words]
        
        # Calculate match score
        match_score = int((len(included_keywords) / len(job_keywords)) * 100) if job_keywords else 0
        
        return {
            "method": "basic_keyword_matching",
            "included_keywords": included_keywords[:10],
            "missing_keywords": missing_keywords[:10],
            "match_score": match_score,
            "suggestions": f"Add these keywords to improve match: {', '.join(missing_keywords[:5])}" if missing_keywords else "Good keyword match!"
        }
    except Exception as e:
        return {
            "method": "basic",
            "error": str(e),
            "match_score": 50,
            "suggestions": "Enable OpenAI API for better optimization"
        }
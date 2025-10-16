import os
from typing import Optional

def generate_cover_letter(application_id: str, db) -> str:
    """
    Generate cover letter using OpenAI GPT or fallback template
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        return _generate_with_gpt(application_id, db, openai_key)
    else:
        return _generate_with_template(application_id, db)

def _generate_with_gpt(application_id: str, db, api_key: str) -> str:
    """Generate cover letter using OpenAI GPT"""
    try:
        import openai
        openai.api_key = api_key
        
        # Get application details from database
        application = db.exec(
            "SELECT * FROM application WHERE id = ?", 
            (application_id,)
        ).first()
        
        if not application:
            return "Application not found"
        
        prompt = f"""
        Write a professional cover letter for this job application:
        
        Position: {application.title}
        Company: {application.company}
        Job Description: {application.description[:1000]}
        
        Write a compelling cover letter that highlights relevant experience
        and shows enthusiasm for the role. Keep it professional and concise.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return _generate_with_template(application_id, db)

def _generate_with_template(application_id: str, db) -> str:
    """Generate cover letter using basic template"""
    application = db.exec(
        "SELECT * FROM application WHERE id = ?", 
        (application_id,)
    ).first()
    
    if not application:
        return "Application not found"
    
    return f"""
    Dear Hiring Manager,
    
    I am writing to express my interest in the {application.title} position at {application.company}. 
    With my background and experience, I believe I would be a valuable asset to your team.
    
    [Your specific qualifications and enthusiasm for the role]
    
    Thank you for considering my application. I look forward to the opportunity to discuss 
    how I can contribute to {application.company}'s success.
    
    Sincerely,
    [Your Name]
    """

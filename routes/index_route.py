# routes/index_route.py
from flask import render_template, session

def index_page(): # Renamed to avoid conflict if imported directly as 'index'
    
    print("INFO: index_page() route was hit.")
    form_data = {
        'job_description': session.get('last_jd', ''),
        'job_title': session.get('last_job_title', 'Tailored'),
        'company': session.get('last_company', 'Resume'),
        'model_tailoring': session.get('last_model_tailoring', 'gemini-1.5-flash'),
        'model_ats': session.get('last_model_ats', 'gemini-1.5-flash'),
        'model_evaluator': session.get('last_model_evaluator', 'gemini-1.5-flash'),
        'model_cover_letter': session.get('last_model_cover_letter', 'gemini-1.5-flash'),
        'generate_cover_letter': session.get('last_generate_cover_letter', False)
    }
    return render_template("form.html", form_data=form_data)


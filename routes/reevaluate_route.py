# routes/reevaluate_route.py
from flask import request, session, current_app # Added current_app
import json
import os # Added os
import bleach

# Assuming utils.py is in the same 'routes' package or adjust import
try:
    from .utils import get_plain_text_from_html
except ImportError:
    import re # Fallback
    from bs4 import BeautifulSoup
    print("WARN: [reevaluate_route] Using fallback get_plain_text_from_html. Ensure utils.py is correctly set up.")
    def get_plain_text_from_html(html_content: str) -> str:
        if not html_content: return ""
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

from modules.resume_evaluator import evaluate_resume # Ensure this is the correct path

def reevaluate_resume_logic(): # Renamed for consistency
    print("INFO: [/reevaluate_resume] - Re-evaluation request received.")
    data = request.get_json()
    if not data or 'resume_html' not in data:
        print("ERROR: [/reevaluate_resume] - Bad request: resume_html missing.")
        return json.dumps({"error": "Missing resume_html in request"}), 400

    raw_edited_resume_html = data['resume_html']

    # Sanitize user-edited HTML
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'ul', 'ol', 'li', 'strong', 'em', 'u', 'span', 'div', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
    allowed_attributes = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, '*': ['style', 'class', 'id']}
    sanitized_resume_html = bleach.clean(raw_edited_resume_html, tags=allowed_tags, attributes=allowed_attributes, strip=True)
    
    resume_plain_text = get_plain_text_from_html(sanitized_resume_html)
    print(f"INFO: [/reevaluate_resume] - Plain text for re-evaluation (first 200 chars): {resume_plain_text[:200]}...")

    # --- Retrieve the cleaned job description ID from session and read from file ---
    jd_file_id = session.get('last_cleaned_jd_id') 
    if not jd_file_id:
        print("ERROR: [/reevaluate_resume] - last_cleaned_jd_id not found in session.")
        return json.dumps({"error": "Job description session ID not found for re-evaluation. Please start over."}), 500
    
    temp_data_folder = current_app.config['TEMP_DATA_FOLDER']
    jd_temp_path = os.path.join(temp_data_folder, f"jd_{jd_file_id}.txt")
    jd_clean = None
    try:
        print(f"INFO: [/reevaluate_resume] - Reading jd_clean from: {jd_temp_path}")
        with open(jd_temp_path, 'r', encoding='utf-8') as f:
            jd_clean = f.read()
    except FileNotFoundError:
        print(f"ERROR: [/reevaluate_resume] - Cleaned JD temp file not found: {jd_temp_path}")
        return json.dumps({"error": "Job description data file not found. Please start over."}), 404
    except Exception as e:
        print(f"ERROR: [/reevaluate_resume] - Error reading cleaned JD temp file: {e}")
        return json.dumps({"error": f"Error reading job description data: {str(e)}"}), 500
    
    if not jd_clean: # Should be caught by FileNotFoundError, but good check
        print("ERROR: [/reevaluate_resume] - jd_clean is empty after attempting to read from file.")
        return json.dumps({"error": "Failed to load job description for re-evaluation."}), 500
    # --- End JD retrieval ---
    
    evaluator_model = session.get('last_model_evaluator', 'gemini-1.5-flash')
    print(f"INFO: [/reevaluate_resume] - Using evaluator model: {evaluator_model}, JD (first 50): {jd_clean[:50]}...")

    try:
        new_feedback = evaluate_resume(resume_plain_text, jd_clean, model=evaluator_model)
        print("INFO: [/reevaluate_resume] - New feedback generated.")
        return json.dumps({"new_feedback": new_feedback})
    except Exception as e:
        print(f"ERROR: [/reevaluate_resume] - Error during evaluate_resume call: {e}")
        # import traceback
        # traceback.print_exc() # For detailed error from evaluate_resume module
        return json.dumps({"error": f"Failed to re-evaluate: {str(e)}"}), 500
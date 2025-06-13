# routes/generate_route.py
from flask import render_template, request, session, current_app
import os
import json
import uuid
import markdown2
try:
    from .utils import clean_llm_markdown_output, get_plain_text_from_html
except ImportError:
    # Fallback definitions if utils.py is not found or for standalone testing
    import re
    from bs4 import BeautifulSoup
    print("WARN: [generate_route] Using fallback helper functions. Ensure utils.py is correctly set up.")
    def clean_llm_markdown_output(output_str: str) -> str:
        if not output_str: return ""
        return re.sub(r"^```(?:markdown)?\s*|\s*```$", "", output_str.strip(), flags=re.IGNORECASE | re.MULTILINE)
    def get_plain_text_from_html(html_content: str) -> str:
        if not html_content: return ""
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

from modules.resume_parser import get_parsed_resume
from modules.jd_parser import clean_job_description
from modules.tailor_agent import generate_tailored_resume
from modules.ats_optimizer import score_ats_match
from modules.resume_evaluator import evaluate_resume
from modules.cover_letter_agent import generate_cover_letter
from .utils import cleanup_temp_files
# generate_pdf_resume is called by download_pdf_route

def generate_logic():
    print("======== /GENERATE ROUTE LOGIC CALLED ========")
    upload_folder = current_app.config['UPLOAD_FOLDER']
    temp_data_folder = current_app.config['TEMP_DATA_FOLDER']

    # Check and print the effective secret key for debugging session issues
    # print(f"DEBUG: [/generate_logic] EFFECTIVE SECRET KEY: {current_app.secret_key}")


    resume_file = request.files.get("resume")
    if resume_file and resume_file.filename.endswith(".docx"):
        if not os.path.exists(upload_folder): os.makedirs(upload_folder)
        resume_path = os.path.join(upload_folder, "master_resume.docx")
        resume_file.save(resume_path)
        print(f"INFO: Saved uploaded resume to {resume_path}")

    raw_jd = request.form.get("job_description", "") # Default to empty string
    job_title_from_form = request.form.get("job_title", "Job")
    company_from_form = request.form.get("company", "Company")
    jd_clean = clean_job_description(raw_jd)

    models = {
        "tailoring": request.form.get("model_tailoring"),
        "ats": request.form.get("model_ats"),
        "evaluator": request.form.get("model_evaluator"),
        "cover_letter": request.form.get("model_cover_letter")
    }
    want_cover_letter = request.form.get("generate_cover_letter") == "yes"

    # --- Store values in session & temp files ---
    # Small items directly in session:
    # session['last_jd_for_form'] = raw_jd # For re-populating form (if not too large, otherwise also use temp file)
    session['last_job_title_for_pdf'] = job_title_from_form
    session['last_company_for_pdf'] = company_from_form
    session['last_model_tailoring'] = models["tailoring"]
    session['last_model_ats'] = models["ats"]
    session['last_model_evaluator'] = models["evaluator"]
    session['last_model_cover_letter'] = models["cover_letter"]
    session['last_generate_cover_letter_pref'] = want_cover_letter

    # Large items (jd_clean, original_parsed_resume) go into temp files, store IDs in session:
    jd_file_id = str(uuid.uuid4())
    jd_temp_path = os.path.join(temp_data_folder, f"jd_{jd_file_id}.txt")
    try:
        with open(jd_temp_path, 'w', encoding='utf-8') as f:
            f.write(jd_clean)
        session['last_cleaned_jd_id'] = jd_file_id # STORE ID
        print(f"INFO: Stored cleaned JD in temp file ID: {jd_file_id}")
    except Exception as e:
        print(f"ERROR: Failed to write jd_clean to temp file: {e}")
        # Handle error appropriately, maybe return error to user
        return "Error saving job description data.", 500


    original_parsed_resume = get_parsed_resume(model=models["tailoring"], force_parse=bool(resume_file))
    if "error" in original_parsed_resume or not isinstance(original_parsed_resume, dict):
        error_msg = original_parsed_resume.get('error', 'Original parsed resume error.')
        print(f"ERROR: Parsing original resume: {error_msg}")
        return f"❌ Error parsing original resume: {error_msg}"
    
    opr_file_id = str(uuid.uuid4())
    opr_temp_path = os.path.join(temp_data_folder, f"opr_{opr_file_id}.json")
    try:
        with open(opr_temp_path, 'w', encoding='utf-8') as f:
            json.dump(original_parsed_resume, f)
        session['original_parsed_resume_id'] = opr_file_id # STORE ID
        # print(f"INFO: Original parsed resume stored in temp file ID: {opr_file_id}. Keys: {list(original_parsed_resume.keys())}")
    except Exception as e:
        print(f"ERROR: Failed to write original_parsed_resume to temp file: {e}")
        return "Error saving original resume data.", 500
    # --- End session/temp file storage for inputs to other routes ---
    
    tailored_resume_markdown_str_raw = generate_tailored_resume(original_parsed_resume, jd_clean, model=models["tailoring"])
    tailored_resume_markdown_str = clean_llm_markdown_output(tailored_resume_markdown_str_raw)
    print(f"INFO: Tailored resume MARKDOWN (first 300 chars):\n{tailored_resume_markdown_str[:300]}...")

    try:
        tailored_resume_html = markdown2.markdown(tailored_resume_markdown_str, extras=["smarty", "break-on-newline", "fenced-code-blocks", "tables", "nofollow", "cuddled-lists"])
    except Exception as e:
        print(f"ERROR converting Markdown to HTML: {e}")
        tailored_resume_html = f"<p>Error converting resume to displayable format.</p><pre>{tailored_resume_markdown_str}</pre>"
    
    text_for_downstream_modules = get_plain_text_from_html(tailored_resume_html)
    
    ats_result = score_ats_match(text_for_downstream_modules, jd_clean)
    evaluator_feedback = evaluate_resume(text_for_downstream_modules, jd_clean, model=models["evaluator"])
    
    cover_letter_html = ""
    if want_cover_letter:
        cover_letter_markdown = generate_cover_letter(text_for_downstream_modules, jd_clean, model=models["cover_letter"])
        if cover_letter_markdown:
             cover_letter_html = markdown2.markdown(cover_letter_markdown, extras=["smarty", "break-on-newline"])

    # --- Prepare and store data specifically for the PDF generation of the CURRENTLY tailored resume ---
    pdf_content_temp_file_id = str(uuid.uuid4())
    pdf_content_temp_path = os.path.join(temp_data_folder, f"pdf_{pdf_content_temp_file_id}.json")
    
    applicant_name = "Applicant" 
    if isinstance(original_parsed_resume, dict): # Using original_parsed_resume to get name
        name_keys_to_try = ["Name", "Full Name", "Applicant Name", "Applicant"] 
        name_keys_to_try += [k for k in original_parsed_resume.keys() if "name" in k.lower() and isinstance(original_parsed_resume[k], str)]
        name_keys_to_try += [k for k in original_parsed_resume.keys() if any(n_part in k.lower() for n_part in ['acharya','gautam']) and isinstance(original_parsed_resume[k], str)]
        for nk in name_keys_to_try:
            name_val = original_parsed_resume.get(nk)
            if isinstance(name_val, str):
                potential_name = name_val.split("|")[0].strip()
                if potential_name and len(potential_name.split()) < 5 : 
                    applicant_name = potential_name
                    break 
        if applicant_name == "Applicant" and "raw_text" in original_parsed_resume:
             applicant_name = original_parsed_resume["raw_text"].split("\n")[0].strip()
    session['last_applicant_name_for_pdf'] = applicant_name # Small, ok for session

    pdf_gen_data = {
        "name": applicant_name, 
        "job_title": job_title_from_form, 
        "company": company_from_form,     
        "original_tailored_resume_html": tailored_resume_html # The HTML of THIS tailored version
    }
    try:
        with open(pdf_content_temp_path, 'w', encoding='utf-8') as f:
            json.dump(pdf_gen_data, f)
        session['pdf_temp_file_id'] = pdf_content_temp_file_id # Store ID for THIS PDF content
        print(f"INFO: PDF content data saved to temp file ID: {session['pdf_temp_file_id']}")
    except Exception as e:
        print(f"ERROR: Failed to write PDF content data to temp file: {e}")
        return "Error saving PDF data.", 500
    # --- End PDF data storage ---
    
        # --- Call Cleanup Function ---
    try:
        temp_data_folder_for_cleanup = current_app.config['TEMP_DATA_FOLDER']
        cleanup_log_output = cleanup_temp_files(temp_data_folder_for_cleanup, max_files_to_keep_per_prefix=5) # Adjust max_files as needed
        # print(cleanup_log_output) 
        print(f"INFO: [/generate_logic] Cleanup ran with or without issues.")
    except Exception as e_cleanup:
        print(f"ERROR: [/generate_logic] - Exception during temp file cleanup: {e_cleanup}")
    # --- End Cleanup Call ---
    section_titles_for_dropdown = list(original_parsed_resume.keys()) if isinstance(original_parsed_resume, dict) else []
    
    # print(f"DEBUG: [/generate_logic] FULL SESSION before render_template (should be small now): {dict(session)}")
    return render_template("result.html",
        tailored_resume_html=tailored_resume_html,
        ats_score=ats_result["ats_score"],
        matched_keywords=ats_result["matched_keywords"],
        missing_keywords=ats_result["missing_keywords"],
        evaluator_feedback=evaluator_feedback,
        cover_letter_html=cover_letter_html,
        section_titles_for_dropdown=section_titles_for_dropdown
    )
# routes/download_pdf_route.py
from flask import request, session, send_file, current_app as app
import io
import os
import json
import bleach 
from modules.pdf_generator import generate_pdf_resume


def download_pdf_logic():
    temp_data_folder = app.config['TEMP_DATA_FOLDER']
    print("======== /DOWNLOAD_PDF LOGIC CALLED ========")
    temp_data_folder = app.config['TEMP_DATA_FOLDER']
    
    # Initialize variables that will be populated based on the path taken
    resume_html_to_render = ""
    name_for_pdf = "Applicant"
    job_title_for_pdf = "Job"
    company_for_pdf = "Company"
    is_edited_version = False

    use_edited_content_flag = request.form.get("use_edited_content") == "true"
    use_original_tailored_flag = request.form.get("use_original_tailored") == "true"

    print(f"INFO: /download_pdf: use_edited={use_edited_content_flag}, use_original={use_original_tailored_flag}")

    if use_edited_content_flag:
        print("INFO: Generating PDF from EDITED HTML content from form.")
        raw_edited_html = request.form.get("edited_resume_html")
        if not raw_edited_html:
            return "Error: No edited resume HTML content received.", 400
        
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'ul', 'ol', 'li', 'strong', 'em', 'u', 'span', 'div', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
        allowed_attributes = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, '*': ['style', 'class', 'id']}
        resume_html_to_render = bleach.clean(raw_edited_html, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        
        # Retrieve name, job_title, company FOR THE PDF from session values set during original /generate
        name_for_pdf = session.get('last_applicant_name_for_pdf', 'Edited_Applicant')
        job_title_for_pdf = session.get('last_job_title_for_pdf', 'Edited_Job')
        company_for_pdf = session.get('last_company_for_pdf', 'Edited_Company')
        is_edited_version = True
        print(f"INFO: Using for EDITED PDF - Name: {name_for_pdf}, Job: {job_title_for_pdf}, Co: {company_for_pdf}")
    
    elif use_original_tailored_flag:
        print("INFO: Generating PDF from ORIGINAL tailored HTML content (from temp file).")
        retrieved_pdf_content_id = session.get('pdf_temp_file_id') # Using a more descriptive name
        
        if not retrieved_pdf_content_id: 
            print("ERROR: PDF temp_file_id (retrieved_pdf_content_id) not found in session for original PDF download.")
            return "Error: PDF session ID not found for original. Please re-generate.", 400
        
        temp_data_path = os.path.join(temp_data_folder, f"pdf_{retrieved_pdf_content_id}.json") 
        print(f"INFO: Constructed temp_data_path for original PDF: {temp_data_path}") # Log the path being checked

        if not os.path.exists(temp_data_path): 
            print(f"ERROR: PDF data file missing for original at the constructed path: {temp_data_path}")
            return "Error: PDF data file missing. Please re-generate.", 404
        try:
            with open(temp_data_path, 'r', encoding='utf-8') as f: 
                pdf_gen_data = json.load(f)
            print(f"INFO: Successfully loaded PDF data from {temp_data_path}")
        except Exception as e:
            print(f"ERROR: Reading PDF temp data from {temp_data_path}: {e}")
            return f"Error reading PDF data: {str(e)}", 500
        
        resume_html_to_render = pdf_gen_data.get("original_tailored_resume_html")
        name_for_pdf = pdf_gen_data.get("name", "Applicant")
        job_title_for_pdf = pdf_gen_data.get("job_title", "Job")
        company_for_pdf = pdf_gen_data.get("company", "Company")
        # is_edited_version remains False
        print(f"INFO: Using for ORIGINAL PDF - Name: {name_for_pdf}, Job: {job_title_for_pdf}, Co: {company_for_pdf}")

    else:
        print("ERROR: PDF download request flags unclear. Neither original nor edited specified.")
        return "Error: PDF download request is unclear (no edit/original flag).", 400

    if not resume_html_to_render:
        print("ERROR: Resume HTML content is effectively missing for PDF generation.")
        return "Error: Resume HTML content is missing for PDF generation.", 500

    print(f"INFO: Calling generate_pdf_resume for '{name_for_pdf}'")
    # Pass the correctly determined name, job_title, company to the PDF generator
    pdf_bytes = generate_pdf_resume(resume_html_to_render, name_for_pdf, job_title_for_pdf, company_for_pdf, return_bytes=True)

    if pdf_bytes:
        safe_name = name_for_pdf.replace(" ", "_").strip() if name_for_pdf else "applicant"
        safe_company = company_for_pdf.replace(" ", "_").replace("/", "-").strip() if company_for_pdf else "company"
        safe_job_title = job_title_for_pdf.replace(" ", "_").replace("/", "-").strip() if job_title_for_pdf else "job"
        version_suffix = "_Edited" if is_edited_version else ""
        download_filename = f"{safe_name}_{safe_job_title}_{safe_company}_Resume{version_suffix}.pdf"
        
        print(f"INFO: Sending PDF: {download_filename}")
        return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=download_filename)
    else:
        print("ERROR: PDF generation returned no bytes.")
        return "Error generating PDF.", 500
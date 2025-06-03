# routes/retailor_route.py
from flask import request, session, current_app
import json
import os
import markdown2

# Assuming utils.py is in the same 'routes' package or adjust import
try:
    from .utils import clean_llm_markdown_output
except ImportError:
    import re # Fallback
    print("WARN: [retailor_route] Using fallback clean_llm_markdown_output. Ensure utils.py is correctly set up.")
    def clean_llm_markdown_output(output_str: str) -> str:
        if not output_str: return ""
        return re.sub(r"^```(?:markdown)?\s*|\s*```$", "", output_str.strip(), flags=re.IGNORECASE | re.MULTILINE)

from modules.tailor_agent import generate_tailored_resume # Your tailoring LLM call

def retailor_section_logic(): # Changed from retailor_section
    print("INFO: [/retailor_section] - Re-tailor section request received.")
    data = request.get_json()
    if not data or "section_name" not in data:
        print("ERROR: [/retailor_section] - Bad request: 'section_name' missing.")
        return json.dumps({"error": "Bad request: 'section_name' missing"}), 400

    target_section_for_output = data.get("section_name") # This is "all_sections" or "Experience", etc.
    temp_data_folder = current_app.config['TEMP_DATA_FOLDER']

    # --- Retrieve IDs from session ---
    opr_file_id = session.get('original_parsed_resume_id')
    jd_file_id = session.get('last_cleaned_jd_id')
    tailor_model_pref = session.get('last_model_tailoring', 'gemini-1.5-flash')

    if not opr_file_id or not jd_file_id:
        error_msg = []
        if not opr_file_id: error_msg.append("original_parsed_resume_id")
        if not jd_file_id: error_msg.append("last_cleaned_jd_id")
        missing_data = ", ".join(error_msg)
        print(f"ERROR: [/retailor_section] - Session data missing for re-tailoring: {missing_data}")
        return json.dumps({"error": f"Session data missing ({missing_data}). Please start over."}), 500

    # --- Construct file paths and read data (FULL original resume and JD) ---
    opr_temp_path = os.path.join(temp_data_folder, f"opr_{opr_file_id}.json")
    jd_temp_path = os.path.join(temp_data_folder, f"jd_{jd_file_id}.txt")

    full_original_parsed_resume_data = None # Renamed for clarity
    jd_clean_for_retailor = None           # Renamed for clarity

    try:
        print(f"INFO: [/retailor_section] - Reading full_original_parsed_resume_data from: {opr_temp_path}")
        with open(opr_temp_path, 'r', encoding='utf-8') as f:
            full_original_parsed_resume_data = json.load(f)
        
        print(f"INFO: [/retailor_section] - Reading jd_clean_for_retailor from: {jd_temp_path}")
        with open(jd_temp_path, 'r', encoding='utf-8') as f:
            jd_clean_for_retailor = f.read()
    except FileNotFoundError as fnf_e:
        print(f"ERROR: [/retailor_section] - Required data file not found: {fnf_e.filename}")
        return json.dumps({"error": "Required data files not found. Please start over."}), 404
    except Exception as e:
        print(f"ERROR: [/retailor_section] - Error reading data for re-tailoring: {e}")
        return json.dumps({"error": f"Error reading data for re-tailoring: {str(e)}"}), 500
    
    if not full_original_parsed_resume_data or not jd_clean_for_retailor:
        print("ERROR: [/retailor_section] - Failed to load full_original_parsed_resume_data or jd_clean after file read attempt.")
        return json.dumps({"error": "Failed to load critical data for re-tailoring."}), 500
    # --- End data retrieval ---

    # Check if the target section (if not "all_sections") actually exists in the full resume
    if target_section_for_output != "all_sections" and target_section_for_output not in full_original_parsed_resume_data:
        print(f"ERROR: [/retailor_section] - Target section '{target_section_for_output}' not found in original resume data.")
        return json.dumps({"error": f"Specified section '{target_section_for_output}' not found in original resume data."}), 400

    try:
        print(f"INFO: [/retailor_section] - Calling generate_tailored_resume. Passing FULL resume for context. Target section for OUTPUT: '{target_section_for_output}'.")
        
        # ALWAYS pass the full original resume data for context.
        # The `target_section` parameter tells the LLM which section(s) to focus its *output* on.
        new_tailored_markdown_raw = generate_tailored_resume(
            resume_data_dict=full_original_parsed_resume_data,
            jd_text=jd_clean_for_retailor, 
            model=tailor_model_pref,
            target_section=target_section_for_output # Instructs LLM on the scope of its Markdown output
        )
        new_tailored_markdown = clean_llm_markdown_output(new_tailored_markdown_raw)
        # This HTML will contain Markdown for "all_sections" or *just* the "target_section_for_output"
        new_section_or_full_html = markdown2.markdown(new_tailored_markdown, extras=["smarty", "break-on-newline", "fenced-code-blocks", "tables", "nofollow", "cuddled-lists"])

        response_data = {}
        is_full_retailor_output = (target_section_for_output == "all_sections")

        if is_full_retailor_output:
            response_data = {"new_full_resume_html": new_section_or_full_html}
            
            # Update the temp file for the "Download Initial PDF" button
            pdf_content_temp_file_id = session.get('pdf_temp_file_id')
            if pdf_content_temp_file_id:
                pdf_content_temp_path = os.path.join(temp_data_folder, f"pdf_{pdf_content_temp_file_id}.json")
                if os.path.exists(pdf_content_temp_path):
                    try:
                        with open(pdf_content_temp_path, 'r', encoding='utf-8') as f: pdf_gen_data_orig = json.load(f)
                        pdf_gen_data_orig['original_tailored_resume_html'] = new_section_or_full_html 
                        with open(pdf_content_temp_path, 'w', encoding='utf-8') as f: json.dump(pdf_gen_data_orig, f)
                        print(f"INFO: [/retailor_section] - Updated temp PDF data file ({pdf_content_temp_path}) with new full HTML after 'all_sections' re-tailor.")
                    except Exception as e_tf_update:
                        print(f"WARN: [/retailor_section] - Could not update temp PDF data file: {e_tf_update}")
                # else: No need to create it here if it doesn't exist, generate_logic handles initial creation.
            # else: No pdf_temp_file_id in session, can't update.
        else: # Only a specific section was re-tailored and returned by LLM
            response_data = {
                "updated_section_title": target_section_for_output, 
                "updated_section_html": new_section_or_full_html # HTML for *only* the re-tailored section
            }
        
        print(f"INFO: [/retailor_section] - Re-tailoring complete. Sending response: {list(response_data.keys())}")
        return json.dumps(response_data)

    except Exception as e:
        print(f"ERROR: [/retailor_section] - Error during re-tailoring: {e}")
        # import traceback; traceback.print_exc() # Uncomment for full traceback
        return json.dumps({"error": f"Failed to re-tailor: {str(e)}"}), 500
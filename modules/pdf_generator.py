# modules/pdf_generator.py
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

def generate_pdf_resume(resume_html_content_str, name, job_title, company, output_dir="output_pdfs", return_bytes=False):
    """
    Converts tailored resume (provided as an HTML string) to styled PDF
    using a basic Jinja2 + HTML template to wrap the content and apply styles.
    """
    env = Environment(loader=FileSystemLoader("templates"))
    # This template now primarily provides the <head> with styles and <body> wrapper
    template = env.get_template("resume_pdf_wrapper_template.html") 

    # The resume_html_content_str is the Markdown-converted, tailored resume HTML
    rendered_page_html = template.render(
        applicant_name=name,
        # job_title_for_header=job_title, # If your wrapper needs these
        # company_for_header=company,
        resume_body_html=resume_html_content_str # The core HTML content
    )

    if return_bytes:
        pdf_bytes = HTML(string=rendered_page_html).write_pdf()
        return pdf_bytes
    else:
        # ... (file saving logic - ensure output_dir is defined or passed) ...
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        safe_name = name.replace(" ", "_").lower()
        safe_company = company.replace(" ", "_").lower()
        filename = f"{safe_name}_{safe_company}_resume.pdf"
        output_path = os.path.join(output_dir, filename)
        HTML(string=rendered_page_html).write_pdf(output_path)
        return output_path
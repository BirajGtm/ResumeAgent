# routes/main_routes.py
from flask import Blueprint

# Import the logic functions from your individual route files
from .index_route import index_page
from .generate_route import generate_logic
from .download_pdf_route import download_pdf_logic
from .reevaluate_route import reevaluate_resume_logic
from .retailor_route import retailor_section_logic


main_bp = Blueprint(
    'main_bp', 
    __name__,
    template_folder='templates',
    static_folder='../static' 
)

# Register routes using the imported logic functions
main_bp.add_url_rule('/', view_func=index_page, methods=['GET'])
main_bp.add_url_rule('/generate', view_func=generate_logic, methods=['POST'])
main_bp.add_url_rule('/download_pdf', view_func=download_pdf_logic, methods=['POST'])
main_bp.add_url_rule('/reevaluate_resume', view_func=reevaluate_resume_logic, methods=['POST'])
main_bp.add_url_rule('/retailor_section', view_func=retailor_section_logic, methods=['POST'])
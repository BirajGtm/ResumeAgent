# routes/main_routes.py
from flask import Blueprint

# Import the logic functions from your individual route files
from .index_route import index_page
from .generate_route import generate_logic
from .download_pdf_route import download_pdf_logic
from .reevaluate_route import reevaluate_resume_logic
from .retailor_route import retailor_section_logic# Assuming utils.py is in the same package

# You might want to put shared helper functions (clean_llm_markdown_output, get_plain_text_from_html)
# in a separate routes/utils.py or keep them here if not too many.
# For this example, I'll assume they are accessible or defined where needed.
# Let's define them here for now if they are not in a utils.py already used by individual routes.

main_bp = Blueprint(
    'main_bp', 
    __name__,
    template_folder='../templates', # Correctly points one level up to 'templates'
    static_folder='../static'      # Correctly points one level up to 'static'
)

# Register routes using the imported logic functions
main_bp.add_url_rule('/', view_func=index_page, methods=['GET'])
main_bp.add_url_rule('/generate', view_func=generate_logic, methods=['POST'])
main_bp.add_url_rule('/download_pdf', view_func=download_pdf_logic, methods=['POST'])
main_bp.add_url_rule('/reevaluate_resume', view_func=reevaluate_resume_logic, methods=['POST'])
main_bp.add_url_rule('/retailor_section', view_func=retailor_section_logic, methods=['POST'])

# Alternative using decorators (if you prefer to define functions here and call logic):
# @main_bp.route('/', methods=['GET'])
# def index_wrapper():
#     return index_page()
#
# @main_bp.route('/generate', methods=['POST'])
# def generate_wrapper():
# return generate_logic()
# ... and so on for other routes. add_url_rule is cleaner if the imported functions
# are designed to be the direct view functions.
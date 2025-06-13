# app.py (Main application file - Lean Version)

from flask import Flask
# from flask_session import Session # Uncomment if using Flask-Session
import os

def create_app():
    app = Flask(__name__) # templates and static folders will be auto-detected if in root

    # --- Configurations ---
    app.config['UPLOAD_FOLDER'] = 'cache' # Relative to instance_path or project root
    app.config['TEMP_DATA_FOLDER'] = 'temp_resume_data'
    
    # IMPORTANT: Set a strong, unique secret key! Get from .env or generate one.
    app.config['SECRET_KEY'] = 'this_is_a_decent_length_secret_key_for_testing_sessions_locally_123!@#' 
    # print(f"EFFECTIVE SECRET KEY: {app.config.get('SECRET_KEY')}")

    # Ensure base folders for app operation exist
    # These paths should be relative to where app.py is, or use absolute paths
    project_root = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(os.path.join(project_root, app.config['UPLOAD_FOLDER'])):
        os.makedirs(os.path.join(project_root, app.config['UPLOAD_FOLDER']))
    if not os.path.exists(os.path.join(project_root, app.config['TEMP_DATA_FOLDER'])):
        os.makedirs(os.path.join(project_root, app.config['TEMP_DATA_FOLDER']))

    # Import and register blueprints
    # Ensure the 'routes' package is in your PYTHONPATH or accessible
    try:
        from routes.main_routes import main_bp # Assuming your blueprint is main_bp in routes/main_routes.py
        app.register_blueprint(main_bp)
        # print("INFO: Main blueprint registered successfully.")
    except ImportError as e:
        print(f"ERROR: Could not import or register blueprint: {e}")
        print("Please ensure routes/main_routes.py exists and main_bp is defined.")
        print("Also check your Python import paths if 'routes' is not found.")


    # You could register other blueprints here if your app grows
    # from routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8000)) 
    # Set debug=False for production deployments!
    app.run(debug=True, host='0.0.0.0', port=port) 
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config

from app.ml_models.predictor import predictor

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    CORS(app)

    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.student import student_bp
    from app.routes.lecturer import lecturer_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create upload folder if not exists
    if not os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads')):
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'))

    # Load ML models
    with app.app_context():
        predictor.load_models()

    # Register custom Jinja filters
    import json
    @app.template_filter('from_json')
    def from_json_filter(s):
        try:
            return json.loads(s) if s else []
        except:
            return []

    @app.template_filter('to_json')
    def to_json_filter(s):
        return json.dumps(s)

    return app
import os
from datetime import timedelta

class Config:
    # Database configuration
    MSSQL_SERVER = os.environ.get('MSSQL_SERVER', '(localdb)\\MSSQLLocalDB')
    MSSQL_DB = os.environ.get('MSSQL_DB', 'smart_academic_system')
    
    # SQLAlchemy MSSQL connection string with Windows Authentication
    # Using raw string for server name to avoid backslash issues
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{MSSQL_SERVER}/{MSSQL_DB}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # File upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'png', 'mp3', 'mp4'}
    
    # ML Models
    ML_MODELS_PATH = 'app/ml_models/models/'
    DROPOUT_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'dropout_model.joblib')
    GRADUATION_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'graduation_model.joblib')
    NEXT_MODULE_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'next_module_model.joblib')
    SCALER_PATH = os.path.join(ML_MODELS_PATH, 'scaler.joblib')
    
    # Feature columns for ML
    FEATURE_COLUMNS = [
        'gender', 'age', 'family_income', 'scholarship', 'distance_from_campus',
        'internet_access', 'attendance_percentage', 'internal_marks', 'assignment_avg',
        'quiz_avg', 'previous_fail_count', 'LMS_login_frequency', 'average_study_hours',
        'forum_participation', 'library_usage', 'current_semester', 'GPA'
    ]
    
    # Risk thresholds
    RISK_THRESHOLD_HIGH = 0.7
    RISK_THRESHOLD_MEDIUM = 0.4
    ATTENDANCE_WARNING_THRESHOLD = 75.0
    
    # Email settings (for alerts simulation)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@smartacademic.com')

    # AI Settings
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini') # gemini, openrouter, or local
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class ProductionConfig(Config):
    DEBUG = False
    # Override with production settings

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vbeu923847529384752938475'

    # Database Configuration
    # Support Render/Heroku postgres:// → postgresql:// fix
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    # Fix for older Heroku/Render postgres:// URIs (SQLAlchemy requires postgresql://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Fix MySQL without driver prefix
    if DATABASE_URL.startswith('mysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
    
    # Fallback to local SQLite if no DATABASE_URL set
    if not DATABASE_URL:
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'freelance.db')
        DATABASE_URL = f'sqlite:///{db_path}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip'}

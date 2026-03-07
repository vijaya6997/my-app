import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vbeu923847529384752938475'

    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    # Fix for Supabase/Heroku/Render postgres:// URIs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Fix MySQL without driver prefix
    if DATABASE_URL.startswith('mysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
    
    # Supabase uses PostgreSQL with connection pooling
    # Add sslmode=require for Supabase if not already present
    if 'supabase' in DATABASE_URL and 'sslmode' not in DATABASE_URL:
        separator = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = DATABASE_URL + separator + 'sslmode=require'
    
    # Fallback to SQLite
    if not DATABASE_URL:
        if os.environ.get('VERCEL'):
            db_path = '/tmp/freelance.db'
        else:
            db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'freelance.db')
        DATABASE_URL = f'sqlite:///{db_path}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pool settings for Supabase/PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
    }

    # Use /tmp/ for uploads on Vercel
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip'}

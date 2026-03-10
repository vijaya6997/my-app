import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vbeu923847529384752938475'

    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    # Fix for Heroku/Render postgres:// URIs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Fix MySQL without driver prefix
    if DATABASE_URL.startswith('mysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
    
    # Fallback to SQLite
    if not DATABASE_URL:
        # Use /tmp/ for Vercel (read-only filesystem outside /tmp/)
        if os.environ.get('VERCEL'):
            db_path = '/tmp/freelance.db'
        else:
            db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'freelance.db')
        DATABASE_URL = f'sqlite:///{db_path}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Use /tmp/ for uploads on Vercel
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip'}

    # Razorpay Payment Gateway (Test Mode Keys)
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_YourRazorpayTestKey')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'YourRazorpayTestSecret')

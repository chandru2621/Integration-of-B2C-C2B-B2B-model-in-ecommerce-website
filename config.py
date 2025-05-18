import os
from datetime import timedelta
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = True  # Enable debug mode
    
    # MySQL Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'ecommerce_db'
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Enable SQL query logging
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'chandrumani260@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'chandrumani260@gmail.com')
    
    # Application settings
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Stripe settings
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'your_stripe_test_key')
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'your_stripe_public_test_key')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'your_webhook_secret') 
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_12984712093847')
    
    # Database Configuration
    # Fallback to SQLite if MySQL configuration is not provided
    MYSQL_USER = os.getenv('DB_USER')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_PORT = os.getenv('DB_PORT', '3306')
    MYSQL_DB = os.getenv('DB_NAME')
    
    if MYSQL_USER and MYSQL_PASSWORD and MYSQL_DB:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        # Fallback to SQLite database in the instance/scratch folder
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'transport.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    
    # Make sure instance and upload folders exist
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

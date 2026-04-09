import os
from datetime import timedelta

class Config:
    _IS_VERCEL = os.environ.get('VERCEL') == '1'
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gruha-alankara-secret-key'

    # Vercel serverless runtime is read-only except /tmp.
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    elif _IS_VERCEL:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/gruha_alankara.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///gruha_alankara.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/tmp/uploads' if _IS_VERCEL else os.path.join(_BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_PERMANENT = True
    
    # AR Configuration
    AR_MODEL_PATH = os.path.join(_BASE_DIR, 'models/ar_models')
    
    # AI Model Configuration
    AI_MODEL_CONFIG = {
        'furniture_detection_model': 'yolov8',
        'style_recommendation_model': 'resnet50',
        'color_palette_model': 'vit'
    }
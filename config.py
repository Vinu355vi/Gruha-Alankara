import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gruha-alankara-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gruha_alankara.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_PERMANENT = True
    
    # AR Configuration
    AR_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models/ar_models')
    
    # AI Model Configuration
    AI_MODEL_CONFIG = {
        'furniture_detection_model': 'yolov8',
        'style_recommendation_model': 'resnet50',
        'color_palette_model': 'vit'
    }
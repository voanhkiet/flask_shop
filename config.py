import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Get database URL from .env
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Fallback to SQLite if not found (useful for local development)
    if  SQLALCHEMY_DATABASE_URI is None:
        SQLALCHEMY_DATABASE_URI = "sqlite:///shop.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Email (Gmail SMTP)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # Uploads
    UPLOAD_FOLDER = "static/uploads/avatars"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

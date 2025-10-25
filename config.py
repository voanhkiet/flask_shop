import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")

    # 🔧 Normalize Postgres URL (Render sometimes gives postgres:// instead of postgresql://)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # ✅ Force use DATABASE_URL — do NOT fallback to SQLite on Render
    if not db_url:
        # Local dev fallback only
        db_url = "sqlite:///shop.db"
        print("⚠️ Using SQLite (local dev fallback)")
    else:
        print("✅ Using PostgreSQL from DATABASE_URL")

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Email
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # File uploads
    UPLOAD_FOLDER = "static/uploads/avatars"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Security — HTTPS-only cookies
SESSION_COOKIE_SECURE = True          # Only send cookies over HTTPS
REMEMBER_COOKIE_SECURE = True         # Flask-Login "remember me" cookies
SESSION_COOKIE_HTTPONLY = True        # Prevent JavaScript access to cookies
REMEMBER_COOKIE_HTTPONLY = True       # Also protect Flask-Login cookies
SESSION_COOKIE_SAMESITE = "Lax"       # Helps prevent CSRF attacks

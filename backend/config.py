"""
config.py — Application configuration classes.
Supports Development, Testing, and Production environments.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""

    # ── Core ────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    APP_NAME = os.environ.get("APP_NAME", "Campus Marketplace")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5000")

    # ── Database ─────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/campus_marketplace"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ── Session ──────────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # Override to True in Production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ── File Uploads ─────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_PRODUCT_IMAGES = 6
    THUMBNAIL_SIZE = (400, 400)
    PROFILE_PICTURE_SIZE = (200, 200)

    # ── Mail ─────────────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # ── School ───────────────────────────────────────────────────────────────
    SCHOOL_EMAIL_DOMAIN = os.environ.get("SCHOOL_EMAIL_DOMAIN", "@up.edu.ph")

    # ── Pagination ───────────────────────────────────────────────────────────
    LISTINGS_PER_PAGE = 12
    MESSAGES_PER_PAGE = 50
    NOTIFICATIONS_PER_PAGE = 20
    USERS_PER_PAGE = 20

    # ── WTForms CSRF ─────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── SocketIO ─────────────────────────────────────────────────────────────
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "threading")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@localhost:5432/campus_marketplace_test"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True


# ── Config selector ──────────────────────────────────────────────────────────
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)

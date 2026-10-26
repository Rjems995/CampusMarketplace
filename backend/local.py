"""Local development configuration and non-destructive database initialization."""

from pathlib import Path
import secrets

from backend.app import create_app
from backend.commands import seed_categories
from backend.config import DevelopmentConfig, PROJECT_ROOT
from backend.extensions import db


def create_local_app(port=5000, instance_dir=None):
    storage = Path(instance_dir or Path(PROJECT_ROOT) / "instance").resolve()
    storage.mkdir(parents=True, exist_ok=True)
    secret_file = storage / ".local-secret"
    try:
        with secret_file.open("x", encoding="utf-8") as handle:
            handle.write(secrets.token_hex(32))
    except FileExistsError:
        pass

    class LocalConfig(DevelopmentConfig):
        DEBUG = False
        SECRET_KEY = secret_file.read_text(encoding="utf-8").strip()
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{(storage / 'local.sqlite3').as_posix()}"
        UPLOAD_FOLDER = str(storage / "uploads")
        SOCKETIO_ASYNC_MODE = "threading"
        SESSION_COOKIE_SECURE = False
        MAIL_SUPPRESS_SEND = True
        MAIL_DEFAULT_SENDER = "local@campus.local"
        LOCAL_MEDIA_ONLY = True
        FRONTEND_URL = f"http://localhost:{port}"

    return create_app(LocalConfig)


def prepare_database(app):
    """Create missing tables/categories; preserve existing records and accounts."""
    with app.app_context():
        db.create_all()
        seed_categories()

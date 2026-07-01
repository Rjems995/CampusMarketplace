"""
utils/helpers.py — Shared utility functions used across the application.
"""

import os
import uuid
import secrets
from datetime import datetime, timedelta
from PIL import Image
from flask import current_app
from slugify import slugify
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)

# ── Image helpers ─────────────────────────────────────────────────────────────

def allowed_image(filename: str) -> bool:
    """Return True if the file extension is in the allowed set."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_image(file_storage, subfolder: str, size: tuple = None) -> str:
    """
    Upload an image to Cloudinary under <subfolder>/, optionally resize it first.
    Returns the full Cloudinary URL (not just a filename).
    """
    img = Image.open(file_storage)

    # Convert RGBA / palette to RGB so JPEG saves cleanly
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if size:
        img.thumbnail(size, Image.LANCZOS)

    # Save resized image to a temporary in-memory buffer
    import io
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", optimize=True, quality=85)
    buffer.seek(0)

    public_id = f"{subfolder}/{uuid.uuid4().hex}"

    result = cloudinary.uploader.upload(
        buffer,
        public_id=public_id,
        overwrite=True,
        resource_type="image",
    )

    return result["secure_url"]


def delete_image(filename: str, subfolder: str) -> None:
    """Delete an image from Cloudinary if it exists."""
    if not filename:
        return

    # filename is actually a full Cloudinary URL now; extract the public_id
    try:
        # URL looks like: https://res.cloudinary.com/<cloud>/image/upload/v.../<subfolder>/<id>.jpg
        parts = filename.split("/")
        # last two segments: subfolder/filename.ext
        public_id = f"{parts[-2]}/{parts[-1].rsplit('.', 1)[0]}"
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass


# ── Slug helpers ──────────────────────────────────────────────────────────────

def unique_slug(title: str, model, max_length: int = 190) -> str:
    """
    Generate a URL-safe slug from *title* that is unique within *model*.
    Appends a random suffix if a collision is detected.
    """
    base = slugify(title)[:max_length]
    slug = base
    counter = 1
    while model.query.filter_by(slug=slug).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# ── Token helpers ─────────────────────────────────────────────────────────────

def generate_token(n_bytes: int = 32) -> str:
    """Return a URL-safe random token string."""
    return secrets.token_urlsafe(n_bytes)


def token_expiry(hours: int = 24) -> datetime:
    """Return a UTC datetime *hours* from now."""
    return datetime.utcnow() + timedelta(hours=hours)


# ── Notification factory ──────────────────────────────────────────────────────

def create_notification(user_id: int, ntype: str, title: str, body: str = None, link: str = None) -> None:
    """
    Persist a Notification row and (if SocketIO is active) push it in real time.
    Import db lazily to avoid circular imports at module load.
    """
    from extensions import db
    from models.notification import Notification

    note = Notification(
        user_id=user_id,
        type=ntype,
        title=title,
        body=body,
        link=link,
    )
    db.session.add(note)
    db.session.commit()

    # Real-time push via SocketIO (best-effort)
    try:
        from extensions import socketio
        socketio.emit(
            "new_notification",
            note.to_dict(),
            room=f"user_{user_id}",
        )
    except Exception:
        pass  # SocketIO not running in test / CLI context


# ── Pagination helper ─────────────────────────────────────────────────────────

def paginate_query(query, page: int, per_page: int):
    """Thin wrapper around SQLAlchemy paginate for consistent error handling."""
    return query.paginate(page=page, per_page=per_page, error_out=False)


# ── Admin log helper ──────────────────────────────────────────────────────────

def log_admin_action(admin_id: int, action: str, target_type: str = None,
                     target_id: int = None, detail: str = None, ip: str = None) -> None:
    from extensions import db
    from models.admin_log import AdminLog

    entry = AdminLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip,
    )
    db.session.add(entry)
    db.session.commit()

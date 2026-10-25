"""
models/user.py — User model with Flask-Login integration.
"""

from datetime import datetime
from flask_login import UserMixin
from backend.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """Represents a registered student or admin."""

    __tablename__ = "users"

    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash  = db.Column(db.String(255), nullable=False)
    first_name     = db.Column(db.String(50), nullable=False)
    last_name      = db.Column(db.String(50), nullable=False)
    is_admin       = db.Column(db.Boolean, default=False)
    is_suspended   = db.Column(db.Boolean, default=False)
    is_verified    = db.Column(db.Boolean, default=False)   # school email verified
    email_confirmed = db.Column(db.Boolean, default=False)  # email confirmed
    remember_token = db.Column(db.String(255))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login     = db.Column(db.DateTime)

    # ── Relationships ─────────────────────────────────────────────────────
    profile        = db.relationship("Profile",       back_populates="user",  uselist=False, cascade="all, delete-orphan")
    products       = db.relationship("Product",       back_populates="seller", cascade="all, delete-orphan")
    favorites      = db.relationship("Favorite",      back_populates="user",  cascade="all, delete-orphan")
    sent_messages  = db.relationship("Message",       foreign_keys="Message.sender_id",   back_populates="sender")
    buyer_convs    = db.relationship("Conversation",  foreign_keys="Conversation.buyer_id",  back_populates="buyer",  cascade="all, delete-orphan")
    seller_convs   = db.relationship("Conversation",  foreign_keys="Conversation.seller_id", back_populates="seller", cascade="all, delete-orphan")
    reviews_given  = db.relationship("Review",        foreign_keys="Review.reviewer_id",  back_populates="reviewer")
    reviews_received = db.relationship("Review",      foreign_keys="Review.reviewee_id",  back_populates="reviewee")
    notifications  = db.relationship("Notification",  back_populates="user",  cascade="all, delete-orphan")
    reports        = db.relationship("Report",        foreign_keys="Report.reporter_id",  back_populates="reporter")
    admin_logs     = db.relationship("AdminLog",      back_populates="admin")
    email_verifications = db.relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
    password_resets     = db.relationship("PasswordReset",     back_populates="user", cascade="all, delete-orphan")

    # ── Password helpers ──────────────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store the password. Never stores plain text."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Return True if password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    # ── Flask-Login ───────────────────────────────────────────────────────
    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_active(self) -> bool:
        """Flask-Login property — suspended users cannot log in."""
        return not self.is_suspended

    # ── Convenience ───────────────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def avatar_url(self) -> str:
        if self.profile and self.profile.profile_picture:
            pic = self.profile.profile_picture
            if pic.startswith("http://") or pic.startswith("https://") or pic.startswith("/"):
                return pic
            return f"/uploads/avatars/{pic}"
        return "/static/images/default-avatar.png"

    @property
    def unread_notification_count(self) -> int:
        return sum(1 for n in self.notifications if not n.is_read)

    @property
    def unread_message_count(self) -> int:
        total = 0
        for conv in self.buyer_convs:
            total += conv.buyer_unread
        for conv in self.seller_convs:
            total += conv.seller_unread
        return total

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "full_name":  self.full_name,
            "email":      self.email,
            "avatar_url": self.avatar_url,
            "is_admin":   self.is_admin,
            "is_online":  self.profile.is_online if self.profile else False,
        }

    def __repr__(self) -> str:
        return f"<User {self.email}>"

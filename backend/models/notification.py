"""models/notification.py"""
from datetime import datetime
from backend.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type       = db.Column(db.String(50), nullable=False)
    title      = db.Column(db.String(120), nullable=False)
    body       = db.Column(db.Text)
    link       = db.Column(db.String(255))
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

    TYPES = {
        "message":    "bi-chat-dots",
        "favorite":   "bi-heart",
        "report":     "bi-flag",
        "sold":       "bi-check-circle",
        "review":     "bi-star",
        "password":   "bi-shield-lock",
        "system":     "bi-bell",
    }

    @property
    def icon(self) -> str:
        return self.TYPES.get(self.type, "bi-bell")

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "type":       self.type,
            "title":      self.title,
            "body":       self.body,
            "link":       self.link,
            "is_read":    self.is_read,
            "icon":       self.icon,
            "created_at": self.created_at.strftime("%b %d, %Y %I:%M %p"),
        }

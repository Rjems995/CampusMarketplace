"""models/admin_log.py"""
from datetime import datetime
from backend.extensions import db


class AdminLog(db.Model):
    __tablename__ = "admin_logs"

    id          = db.Column(db.Integer, primary_key=True)
    admin_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action      = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id   = db.Column(db.Integer)
    detail      = db.Column(db.Text)
    ip_address  = db.Column(db.String(45))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    admin = db.relationship("User", back_populates="admin_logs")

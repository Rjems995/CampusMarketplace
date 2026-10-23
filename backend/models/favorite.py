"""models/favorite.py"""
from datetime import datetime
from backend.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"), nullable=False, index=True)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "product_id"),)

    user    = db.relationship("User",    back_populates="favorites")
    product = db.relationship("Product", back_populates="favorites")

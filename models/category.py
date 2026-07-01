"""models/category.py — Product category."""

from datetime import datetime
from extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), unique=True, nullable=False)
    slug        = db.Column(db.String(80), unique=True, nullable=False, index=True)
    icon        = db.Column(db.String(50), default="bi-tag")
    description = db.Column(db.Text)
    sort_order  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────
    products = db.relationship("Product", back_populates="category")

    @property
    def product_count(self) -> int:
        return sum(1 for p in self.products if p.status == "available")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"

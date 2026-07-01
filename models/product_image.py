"""models/product_image.py"""
from datetime import datetime
from extensions import db


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id          = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    filename    = db.Column(db.String(255), nullable=False)
    is_primary  = db.Column(db.Boolean, default=False)
    sort_order  = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", back_populates="images")

    @property
    def url(self) -> str:
        return self.filename

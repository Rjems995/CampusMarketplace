"""models/product.py — Product (listing) model."""

from datetime import datetime
from extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True)
    seller_id   = db.Column(db.Integer, db.ForeignKey("users.id",      ondelete="CASCADE"),   nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"),  nullable=False, index=True)
    title       = db.Column(db.String(150), nullable=False)
    slug        = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    condition   = db.Column(db.String(30), nullable=False)
    location    = db.Column(db.String(100))
    status      = db.Column(db.String(20), default="available", index=True)
    views       = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_at     = db.Column(db.DateTime)

    # ── Relationships ─────────────────────────────────────────────────────
    seller        = db.relationship("User",         back_populates="products")
    category      = db.relationship("Category",     back_populates="products")
    images        = db.relationship("ProductImage", back_populates="product",  cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    favorites     = db.relationship("Favorite",     back_populates="product",  cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", back_populates="product")
    reviews       = db.relationship("Review",       back_populates="product")
    reports       = db.relationship("Report",       back_populates="product",  foreign_keys="Report.product_id")

    # ── Helpers ───────────────────────────────────────────────────────────
    @property
    def primary_image(self):
        for img in self.images:
            if img.is_primary:
                return img
        return self.images[0] if self.images else None

    @property
    def primary_image_url(self) -> str:
        img = self.primary_image
        if img:
            return f"/uploads/products/{img.filename}"
        return "/static/images/no-image.png"

    @property
    def favorite_count(self) -> int:
        return len(self.favorites)

    @property
    def is_available(self) -> bool:
        return self.status == "available"

    def increment_views(self) -> None:
        self.views = (self.views or 0) + 1

    def mark_sold(self) -> None:
        self.status = "sold"
        self.sold_at = datetime.utcnow()
        if self.seller and self.seller.profile:
            self.seller.profile.total_sales += 1

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "title":       self.title,
            "slug":        self.slug,
            "price":       float(self.price),
            "condition":   self.condition,
            "status":      self.status,
            "image_url":   self.primary_image_url,
            "category":    self.category.name if self.category else None,
            "seller":      self.seller.full_name if self.seller else None,
            "created_at":  self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Product {self.id}: {self.title[:30]}>"

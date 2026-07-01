"""models/review.py"""
from datetime import datetime
from extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id           = db.Column(db.Integer, primary_key=True)
    reviewer_id  = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"),  nullable=False, index=True)
    reviewee_id  = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"),  nullable=False, index=True)
    product_id   = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    rating       = db.Column(db.SmallInteger, nullable=False)
    comment      = db.Column(db.Text)
    is_approved  = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("reviewer_id", "product_id"),)

    reviewer = db.relationship("User",    foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = db.relationship("User",    foreign_keys=[reviewee_id], back_populates="reviews_received")
    product  = db.relationship("Product", back_populates="reviews")

    @property
    def stars_range(self):
        return range(self.rating)

    @property
    def empty_stars_range(self):
        return range(5 - self.rating)

"""models/profile.py — Extended user profile information."""

from datetime import datetime
from extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio             = db.Column(db.Text)
    course          = db.Column(db.String(100))
    year_level      = db.Column(db.String(20))
    school          = db.Column(db.String(150))
    phone           = db.Column(db.String(20))
    location        = db.Column(db.String(100))
    profile_picture = db.Column(db.String(255))
    social_fb       = db.Column(db.String(255))
    average_rating  = db.Column(db.Numeric(3, 2), default=0.00)
    total_reviews   = db.Column(db.Integer, default=0)
    total_sales     = db.Column(db.Integer, default=0)
    is_online       = db.Column(db.Boolean, default=False)
    last_seen       = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────────────
    user = db.relationship("User", back_populates="profile")

    def recalculate_rating(self) -> None:
        """Recompute average_rating and total_reviews from review table."""
        from models.review import Review
        reviews = Review.query.filter_by(reviewee_id=self.user_id, is_approved=True).all()
        self.total_reviews = len(reviews)
        self.average_rating = (
            round(sum(r.rating for r in reviews) / self.total_reviews, 2)
            if self.total_reviews else 0.00
        )

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id}>"

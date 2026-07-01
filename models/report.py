"""models/report.py"""
from datetime import datetime
from extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id          = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"),  nullable=False, index=True)
    product_id  = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True,  index=True)
    reason      = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status      = db.Column(db.String(20), default="pending", index=True)
    admin_note  = db.Column(db.Text)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = db.Column(db.DateTime)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship("User",    foreign_keys=[reporter_id], back_populates="reports")
    product  = db.relationship("Product", foreign_keys=[product_id],  back_populates="reports")
    reviewer = db.relationship("User",    foreign_keys=[reviewed_by])

    REASONS = [
        ("fake_listing",       "Fake Listing"),
        ("spam",               "Spam"),
        ("scam",               "Scam / Fraud"),
        ("offensive_content",  "Offensive Content"),
        ("duplicate",          "Duplicate Listing"),
        ("wrong_category",     "Wrong Category"),
        ("other",              "Other"),
    ]

    @property
    def reason_label(self) -> str:
        return dict(self.REASONS).get(self.reason, self.reason)

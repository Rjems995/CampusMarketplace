"""models/conversation.py"""
from datetime import datetime
from extensions import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id              = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    buyer_id        = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"),  nullable=False, index=True)
    seller_id       = db.Column(db.Integer, db.ForeignKey("users.id",    ondelete="CASCADE"),  nullable=False, index=True)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    buyer_unread    = db.Column(db.Integer, default=0)
    seller_unread   = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("product_id", "buyer_id", "seller_id"),)

    buyer    = db.relationship("User",    foreign_keys=[buyer_id],   back_populates="buyer_convs")
    seller   = db.relationship("User",    foreign_keys=[seller_id],  back_populates="seller_convs")
    product  = db.relationship("Product", back_populates="conversations")
    messages = db.relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    def other_party(self, current_user_id: int):
        return self.seller if self.buyer_id == current_user_id else self.buyer

    def unread_for(self, user_id: int) -> int:
        return self.buyer_unread if user_id == self.buyer_id else self.seller_unread

    def mark_read_for(self, user_id: int) -> None:
        if user_id == self.buyer_id:
            self.buyer_unread = 0
        else:
            self.seller_unread = 0


class Message(db.Model):
    __tablename__ = "messages"

    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id       = db.Column(db.Integer, db.ForeignKey("users.id",         ondelete="CASCADE"), nullable=False, index=True)
    body            = db.Column(db.Text)
    image_filename  = db.Column(db.String(255))
    is_read         = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    conversation = db.relationship("Conversation", back_populates="messages")
    sender       = db.relationship("User",         foreign_keys=[sender_id], back_populates="sent_messages")

    @property
    def image_url(self):
        return self.image_filename

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "sender_id":  self.sender_id,
            "sender_name": self.sender.full_name if self.sender else "Unknown",
            "sender_avatar": self.sender.avatar_url if self.sender else "",
            "body":       self.body,
            "image_url":  self.image_url,
            "is_read":    self.is_read,
            "created_at": self.created_at.strftime("%b %d, %Y %I:%M %p"),
        }

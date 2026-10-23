"""routes/chat.py — Messaging system routes + SocketIO events."""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify, current_app)
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room

from backend.extensions import db, socketio
from backend.models.conversation import Conversation, Message
from backend.models.product import Product
from backend.models.user import User
from backend.utils.helpers import save_image, create_notification
from backend.services.email_service import send_new_message_email
from datetime import datetime

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


# ── Conversation list ─────────────────────────────────────────────────────────

@chat_bp.route("/")
@login_required
def inbox():
    buyer_convs  = (Conversation.query.filter_by(buyer_id=current_user.id)
                    .order_by(Conversation.last_message_at.desc()).all())
    seller_convs = (Conversation.query.filter_by(seller_id=current_user.id)
                    .order_by(Conversation.last_message_at.desc()).all())
    # Merge and deduplicate
    seen = set()
    conversations = []
    for c in sorted(buyer_convs + seller_convs, key=lambda x: x.last_message_at or datetime.min, reverse=True):
        if c.id not in seen:
            seen.add(c.id)
            conversations.append(c)

    return render_template("chat/inbox.html", conversations=conversations, title="Messages")


# ── Open / start a conversation ───────────────────────────────────────────────

@chat_bp.route("/start/<int:product_id>")
@login_required
def start_conversation(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == current_user.id:
        flash("You cannot message yourself.", "warning")
        return redirect(url_for("marketplace.listing_detail", slug=product.slug))

    conv = Conversation.query.filter_by(
        product_id=product_id, buyer_id=current_user.id, seller_id=product.seller_id
    ).first()

    if not conv:
        conv = Conversation(
            product_id=product_id,
            buyer_id=current_user.id,
            seller_id=product.seller_id,
        )
        db.session.add(conv)
        db.session.commit()

    return redirect(url_for("chat.conversation", conv_id=conv.id))


# ── Conversation view ─────────────────────────────────────────────────────────

@chat_bp.route("/<int:conv_id>")
@login_required
def conversation(conv_id):
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        abort(403)

    # Mark messages as read
    conv.mark_read_for(current_user.id)
    Message.query.filter_by(conversation_id=conv_id, is_read=False).filter(
        Message.sender_id != current_user.id
    ).update({"is_read": True})
    db.session.commit()

    messages = Message.query.filter_by(conversation_id=conv_id).order_by(Message.created_at).all()
    other    = conv.other_party(current_user.id)

    return render_template(
        "chat/conversation.html",
        conv=conv,
        messages=messages,
        other=other,
        title=f"Chat with {other.full_name}",
    )


# ── Send message (HTTP fallback) ──────────────────────────────────────────────

@chat_bp.route("/<int:conv_id>/send", methods=["POST"])
@login_required
def send_message(conv_id):
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        abort(403)

    body  = request.form.get("body", "").strip()
    image_file = request.files.get("image")
    image_filename = None

    if image_file and image_file.filename:
        image_filename = save_image(image_file, "messages", size=(800, 800))

    if not body and not image_filename:
        return jsonify({"error": "Empty message"}), 400

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user.id,
        body=body or None,
        image_filename=image_filename,
    )
    db.session.add(msg)

    # Increment unread for recipient
    if current_user.id == conv.buyer_id:
        conv.seller_unread += 1
    else:
        conv.buyer_unread += 1
    conv.last_message_at = msg.created_at

    db.session.commit()

    recipient = conv.other_party(current_user.id)
    create_notification(
        user_id=recipient.id,
        ntype="message",
        title=f"New message from {current_user.full_name}",
        body=body[:80] if body else "📷 Sent an image",
        link=url_for("chat.conversation", conv_id=conv_id),
    )

    return jsonify({"ok": True, "message": msg.to_dict()})


# ── SocketIO events ───────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        if current_user.profile:
            current_user.profile.is_online = True
            db.session.commit()
        emit("status", {"connected": True})


@socketio.on("disconnect")
def on_disconnect():
    if current_user.is_authenticated:
        from datetime import datetime
        if current_user.profile:
            current_user.profile.is_online = False
            current_user.profile.last_seen = datetime.utcnow()
            db.session.commit()


@socketio.on("join_conversation")
def on_join(data):
    conv_id = data.get("conv_id")
    if not conv_id:
        return
    conv = Conversation.query.get(conv_id)
    if conv and current_user.id in (conv.buyer_id, conv.seller_id):
        join_room(f"conv_{conv_id}")


@socketio.on("leave_conversation")
def on_leave(data):
    conv_id = data.get("conv_id")
    if conv_id:
        leave_room(f"conv_{conv_id}")


@socketio.on("send_message")
def on_send_message(data):
    conv_id = data.get("conv_id")
    body    = data.get("body", "").strip()
    if not conv_id or not body:
        return

    conv = Conversation.query.get(conv_id)
    if not conv or current_user.id not in (conv.buyer_id, conv.seller_id):
        return

    msg = Message(
        conversation_id=conv_id,
        sender_id=current_user.id,
        body=body,
    )
    db.session.add(msg)

    if current_user.id == conv.buyer_id:
        conv.seller_unread += 1
    else:
        conv.buyer_unread += 1
    conv.last_message_at = msg.created_at
    db.session.commit()

    # Broadcast to room
    emit("new_message", msg.to_dict(), room=f"conv_{conv_id}")

    # Notify recipient
    recipient = conv.other_party(current_user.id)
    create_notification(
        user_id=recipient.id,
        ntype="message",
        title=f"New message from {current_user.full_name}",
        body=body[:80],
        link=url_for("chat.conversation", conv_id=conv_id),
    )


@socketio.on("typing")
def on_typing(data):
    conv_id = data.get("conv_id")
    if conv_id:
        emit("user_typing", {
            "user_id": current_user.id,
            "name":    current_user.first_name,
        }, room=f"conv_{conv_id}", include_self=False)


@socketio.on("stop_typing")
def on_stop_typing(data):
    conv_id = data.get("conv_id")
    if conv_id:
        emit("user_stop_typing", {"user_id": current_user.id},
             room=f"conv_{conv_id}", include_self=False)

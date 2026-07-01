"""
services/email_service.py — All transactional emails sent by the application.
"""

from flask import current_app, render_template_string
from flask_mail import Message
from extensions import mail


def _send(subject: str, recipients: list, html_body: str) -> None:
    """Low-level send helper. Silently logs errors in development."""
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
    )
    try:
        mail.send(msg)
    except Exception as exc:
        current_app.logger.error("Mail send failed: %s", exc)


# ── Email templates (inline for portability) ──────────────────────────────────

_BASE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 20px; }}
    .card {{ background: #fff; max-width: 560px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
    .header {{ background: #4f46e5; padding: 32px; text-align: center; }}
    .header h1 {{ color: #fff; margin: 0; font-size: 22px; }}
    .body {{ padding: 32px; color: #374151; line-height: 1.6; }}
    .btn {{ display: inline-block; margin: 24px 0; padding: 14px 28px; background: #4f46e5; color: #fff !important; border-radius: 8px; text-decoration: none; font-weight: 600; }}
    .footer {{ text-align: center; padding: 16px; color: #9ca3af; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header"><h1>🎓 Campus Marketplace</h1></div>
    <div class="body">{body}</div>
    <div class="footer">© 2024 Campus Marketplace · This email was sent automatically.</div>
  </div>
</body>
</html>
"""


def send_verification_email(user, token: str) -> None:
    url = f"{current_app.config['FRONTEND_URL']}/auth/verify-email/{token}"
    body = f"""
    <p>Hi {user.first_name},</p>
    <p>Welcome to Campus Marketplace! Please confirm your email address to activate your account.</p>
    <a class="btn" href="{url}">Verify Email Address</a>
    <p>This link expires in <strong>24 hours</strong>.</p>
    <p>If you did not create an account, you can safely ignore this email.</p>
    """
    _send(
        subject="Verify your Campus Marketplace account",
        recipients=[user.email],
        html_body=_BASE.format(body=body),
    )


def send_password_reset_email(user, token: str) -> None:
    url = f"{current_app.config['FRONTEND_URL']}/auth/reset-password/{token}"
    body = f"""
    <p>Hi {user.first_name},</p>
    <p>We received a request to reset your Campus Marketplace password.</p>
    <a class="btn" href="{url}">Reset Password</a>
    <p>This link expires in <strong>1 hour</strong>. If you did not request this, please ignore this email.</p>
    """
    _send(
        subject="Reset your Campus Marketplace password",
        recipients=[user.email],
        html_body=_BASE.format(body=body),
    )


def send_new_message_email(recipient, sender_name: str, product_title: str, conv_id: int) -> None:
    url = f"{current_app.config['FRONTEND_URL']}/chat/{conv_id}"
    body = f"""
    <p>Hi {recipient.first_name},</p>
    <p><strong>{sender_name}</strong> sent you a message about <em>{product_title}</em>.</p>
    <a class="btn" href="{url}">View Message</a>
    """
    _send(
        subject=f"New message from {sender_name}",
        recipients=[recipient.email],
        html_body=_BASE.format(body=body),
    )


def send_listing_sold_email(seller, product_title: str) -> None:
    body = f"""
    <p>Hi {seller.first_name},</p>
    <p>Great news! Your listing <strong>"{product_title}"</strong> has been marked as <strong>Sold</strong>.</p>
    <p>Thank you for using Campus Marketplace!</p>
    """
    _send(
        subject=f'Your listing "{product_title}" is sold!',
        recipients=[seller.email],
        html_body=_BASE.format(body=body),
    )


def send_account_suspended_email(user, reason: str = "") -> None:
    body = f"""
    <p>Hi {user.first_name},</p>
    <p>Your Campus Marketplace account has been <strong>suspended</strong>.</p>
    {"<p>Reason: " + reason + "</p>" if reason else ""}
    <p>If you believe this is a mistake, please contact our support team.</p>
    """
    _send(
        subject="Your Campus Marketplace account has been suspended",
        recipients=[user.email],
        html_body=_BASE.format(body=body),
    )

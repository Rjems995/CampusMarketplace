"""
routes/auth.py — Registration, login, logout, email verification,
forgot/reset password.
"""

from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app)
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models.user import User
from models.profile import Profile
from models.token import EmailVerification, PasswordReset
from forms.auth_forms import (RegistrationForm, LoginForm,
                               ForgotPasswordForm, ResetPasswordForm)
from services.email_service import send_verification_email, send_password_reset_email
from utils.helpers import generate_token, token_expiry

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower().strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        # Create empty profile
        profile = Profile(user_id=user.id)
        db.session.add(profile)

        # Issue email-verification token
        token = generate_token()
        ev = EmailVerification(user_id=user.id, token=token, expires_at=token_expiry(24))
        db.session.add(ev)
        db.session.commit()

        send_verification_email(user, token)

        flash("Account created! Check your email to verify your address.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form, title="Create Account")


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user and user.check_password(form.password.data):
            if user.is_suspended:
                flash("Your account has been suspended. Contact support.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            if user.profile:
                user.profile.is_online = True
            db.session.commit()

            next_page = request.args.get("next")
            return redirect(next_page or url_for("profile.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form, title="Log In")


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    if current_user.profile:
        current_user.profile.is_online = False
        current_user.profile.last_seen = datetime.utcnow()
        db.session.commit()
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# ── Verify Email ──────────────────────────────────────────────────────────────

@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    ev = EmailVerification.query.filter_by(token=token).first()
    if not ev or not ev.is_valid:
        flash("The verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    ev.used = True
    ev.user.email_confirmed = True
    db.session.commit()

    flash("Email verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


# ── Resend Verification ───────────────────────────────────────────────────────

@auth_bp.route("/resend-verification")
@login_required
def resend_verification():
    if current_user.email_confirmed:
        flash("Your email is already verified.", "info")
        return redirect(url_for("profile.dashboard"))

    token = generate_token()
    ev = EmailVerification(user_id=current_user.id, token=token, expires_at=token_expiry(24))
    db.session.add(ev)
    db.session.commit()
    send_verification_email(current_user, token)
    flash("Verification email resent. Check your inbox.", "info")
    return redirect(url_for("profile.dashboard"))


# ── Forgot Password ───────────────────────────────────────────────────────────

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            token = generate_token()
            pr = PasswordReset(user_id=user.id, token=token, expires_at=token_expiry(1))
            db.session.add(pr)
            db.session.commit()
            send_password_reset_email(user, token)
        # Always show same message to prevent email enumeration
        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form, title="Forgot Password")


# ── Reset Password ────────────────────────────────────────────────────────────

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    pr = PasswordReset.query.filter_by(token=token).first()
    if not pr or not pr.is_valid:
        flash("This reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        pr.user.set_password(form.password.data)
        pr.used = True
        db.session.commit()
        flash("Password reset! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, title="Reset Password")

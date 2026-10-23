"""middleware/decorators.py — Route decorators for authorization."""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Allow only admin users; 403 otherwise."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def verified_required(f):
    """
    Redirect to dashboard with a warning if the user's school email
    is not yet verified (is_verified flag).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_verified:
            flash("Please verify your school email to access this feature.", "warning")
            return redirect(url_for("profile.dashboard"))
        return f(*args, **kwargs)
    return decorated


def not_suspended(f):
    """Reject suspended users with a 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_suspended:
            abort(403)
        return f(*args, **kwargs)
    return decorated

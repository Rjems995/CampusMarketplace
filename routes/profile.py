"""routes/profile.py — User dashboard, profile view/edit, favorites, notifications."""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, current_app)
from flask_login import login_required, current_user

from extensions import db
from models.user import User
from models.product import Product
from models.favorite import Favorite
from models.notification import Notification
from models.review import Review
from forms.auth_forms import ChangePasswordForm
from forms.profile_forms import ProfileEditForm
from utils.helpers import save_image, delete_image, create_notification

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


# ── Dashboard ─────────────────────────────────────────────────────────────────

@profile_bp.route("/dashboard")
@login_required
def dashboard():
    my_listings   = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).limit(5).all()
    favorites     = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).limit(5).all()
    notifications = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10).all()
    )
    stats = {
        "active":    Product.query.filter_by(seller_id=current_user.id, status="available").count(),
        "sold":      Product.query.filter_by(seller_id=current_user.id, status="sold").count(),
        "favorites": Favorite.query.filter_by(user_id=current_user.id).count(),
        "reviews":   Review.query.filter_by(reviewee_id=current_user.id, is_approved=True).count(),
    }
    return render_template(
        "profile/dashboard.html",
        my_listings=my_listings,
        favorites=favorites,
        notifications=notifications,
        stats=stats,
        title="Dashboard",
    )


# ── View any profile ──────────────────────────────────────────────────────────

@profile_bp.route("/user/<int:user_id>")
def view_profile(user_id):
    user          = User.query.get_or_404(user_id)
    listings      = Product.query.filter_by(seller_id=user_id, status="available").order_by(Product.created_at.desc()).all()
    sold_listings = Product.query.filter_by(seller_id=user_id, status="sold").order_by(Product.sold_at.desc()).all()
    reviews       = Review.query.filter_by(reviewee_id=user_id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template(
        "profile/view_profile.html",
        viewed_user=user,
        listings=listings,
        sold_listings=sold_listings,
        reviews=reviews,
        title=user.full_name,
    )


# ── Edit profile ──────────────────────────────────────────────────────────────

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileEditForm(obj=current_user.profile)
    form.first_name.data = form.first_name.data or current_user.first_name
    form.last_name.data  = form.last_name.data  or current_user.last_name

    if request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data  = current_user.last_name

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name  = form.last_name.data.strip()

        p = current_user.profile
        p.bio        = form.bio.data
        p.course     = form.course.data
        p.year_level = form.year_level.data
        p.school     = form.school.data
        p.phone      = form.phone.data
        p.location   = form.location.data
        p.social_fb  = form.social_fb.data

        # Profile picture
        if form.profile_picture.data and form.profile_picture.data.filename:
            if p.profile_picture:
                delete_image(p.profile_picture, "avatars")
            p.profile_picture = save_image(
                form.profile_picture.data, "avatars",
                size=current_app.config["PROFILE_PICTURE_SIZE"]
            )

        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile.view_profile", user_id=current_user.id))

    return render_template("profile/edit_profile.html", form=form, title="Edit Profile")


# ── Change password ───────────────────────────────────────────────────────────

@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            create_notification(
                user_id=current_user.id,
                ntype="password",
                title="Password changed",
                body="Your password was updated successfully.",
            )
            flash("Password updated successfully.", "success")
            return redirect(url_for("profile.dashboard"))

    return render_template("profile/change_password.html", form=form, title="Change Password")


# ── My listings ───────────────────────────────────────────────────────────────

@profile_bp.route("/my-listings")
@login_required
def my_listings():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Product.query
        .filter_by(seller_id=current_user.id)
        .order_by(Product.created_at.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )
    return render_template(
        "profile/my_listings.html",
        products=pagination.items,
        pagination=pagination,
        title="My Listings",
    )


# ── Favorites ─────────────────────────────────────────────────────────────────

@profile_bp.route("/favorites")
@login_required
def favorites():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )
    return render_template(
        "profile/favorites.html",
        favorites=pagination.items,
        pagination=pagination,
        title="My Favorites",
    )


# ── Notifications ─────────────────────────────────────────────────────────────

@profile_bp.route("/notifications")
@login_required
def notifications():
    page = request.args.get("page", 1, type=int)
    # Mark all as read when page is opened
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()

    pagination = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=current_app.config["NOTIFICATIONS_PER_PAGE"], error_out=False)
    )
    return render_template(
        "profile/notifications.html",
        notifications=pagination.items,
        pagination=pagination,
        title="Notifications",
    )


# ── Notifications API (JSON) ──────────────────────────────────────────────────

@profile_bp.route("/notifications/unread-count")
@login_required
def unread_count():
    from flask import jsonify
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})

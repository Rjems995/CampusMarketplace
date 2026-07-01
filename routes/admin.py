"""routes/admin.py — Admin dashboard, user management, reports, categories."""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify)
from flask_login import login_required, current_user

from extensions import db
from models.user import User
from models.product import Product
from models.category import Category
from models.report import Report
from models.review import Review
from models.admin_log import AdminLog
from middleware.decorators import admin_required
from utils.helpers import log_admin_action, create_notification
from services.email_service import send_account_suspended_email

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _log(action, target_type=None, target_id=None, detail=None):
    log_admin_action(
        admin_id=current_user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip=request.remote_addr,
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users":       User.query.count(),
        "listings":    Product.query.filter_by(status="available").count(),
        "sold":        Product.query.filter_by(status="sold").count(),
        "reports":     Report.query.filter_by(status="pending").count(),
        "categories":  Category.query.count(),
        "reviews":     Review.query.count(),
    }
    recent_users    = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_listings = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    pending_reports = Report.query.filter_by(status="pending").order_by(Report.created_at.desc()).limit(5).all()
    recent_logs     = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_listings=recent_listings,
        pending_reports=pending_reports,
        recent_logs=recent_logs,
        title="Admin Dashboard",
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    q    = request.args.get("q", "").strip()
    query = User.query
    if q:
        query = query.filter(
            db.or_(User.email.ilike(f"%{q}%"),
                   User.first_name.ilike(f"%{q}%"),
                   User.last_name.ilike(f"%{q}%"))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/users.html", users=pagination.items, pagination=pagination, q=q, title="Manage Users")


@admin_bp.route("/users/<int:user_id>/suspend", methods=["POST"])
@login_required
@admin_required
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot suspend another admin.", "danger")
        return redirect(url_for("admin.users"))
    reason = request.form.get("reason", "")
    user.is_suspended = True
    db.session.commit()
    send_account_suspended_email(user, reason)
    _log("suspend_user", "user", user_id, reason)
    flash(f"{user.full_name} has been suspended.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/unsuspend", methods=["POST"])
@login_required
@admin_required
def unsuspend_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_suspended = False
    db.session.commit()
    _log("unsuspend_user", "user", user_id)
    flash(f"{user.full_name} has been unsuspended.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete an admin account.", "danger")
        return redirect(url_for("admin.users"))
    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    _log("delete_user", "user", user_id, name)
    flash(f"User {name} deleted.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/make-admin", methods=["POST"])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    _log("make_admin", "user", user_id)
    flash(f"{user.full_name} is now an admin.", "success")
    return redirect(url_for("admin.users"))


# ── Listings ──────────────────────────────────────────────────────────────────

@admin_bp.route("/listings")
@login_required
@admin_required
def listings():
    page  = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    query = Product.query
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/listings.html", products=pagination.items, pagination=pagination,
                           status=status, title="Manage Listings")


@admin_bp.route("/listings/<int:product_id>/remove", methods=["POST"])
@login_required
@admin_required
def remove_listing(product_id):
    product = Product.query.get_or_404(product_id)
    product.status = "removed"
    db.session.commit()
    create_notification(
        user_id=product.seller_id,
        ntype="system",
        title="Your listing was removed",
        body=f'"{product.title}" was removed by an admin.',
    )
    _log("remove_listing", "product", product_id, product.title)
    flash("Listing removed.", "info")
    return redirect(url_for("admin.listings"))


@admin_bp.route("/listings/<int:product_id>/feature", methods=["POST"])
@login_required
@admin_required
def feature_listing(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_featured = not product.is_featured
    db.session.commit()
    state = "featured" if product.is_featured else "unfeatured"
    _log(f"{state}_listing", "product", product_id)
    return jsonify({"featured": product.is_featured})


# ── Reports ───────────────────────────────────────────────────────────────────

@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    page   = request.args.get("page", 1, type=int)
    status = request.args.get("status", "pending")
    pagination = (
        Report.query.filter_by(status=status)
        .order_by(Report.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template("admin/reports.html", reports=pagination.items,
                           pagination=pagination, status=status, title="Reports")


@admin_bp.route("/reports/<int:report_id>/review", methods=["POST"])
@login_required
@admin_required
def review_report(report_id):
    report     = Report.query.get_or_404(report_id)
    action     = request.form.get("action")   # "dismiss" | "action"
    admin_note = request.form.get("admin_note", "")
    from datetime import datetime

    report.admin_note  = admin_note
    report.reviewed_by = current_user.id
    report.reviewed_at = datetime.utcnow()

    if action == "action":
        report.status = "actioned"
        if report.product:
            report.product.status = "removed"
    else:
        report.status = "dismissed"

    db.session.commit()
    _log(f"report_{report.status}", "report", report_id)
    flash("Report reviewed.", "success")
    return redirect(url_for("admin.reports"))


# ── Categories ────────────────────────────────────────────────────────────────

@admin_bp.route("/categories")
@login_required
@admin_required
def categories():
    cats = Category.query.order_by(Category.sort_order).all()
    return render_template("admin/categories.html", categories=cats, title="Manage Categories")


@admin_bp.route("/categories/create", methods=["POST"])
@login_required
@admin_required
def create_category():
    from slugify import slugify
    name = request.form.get("name", "").strip()
    icon = request.form.get("icon", "bi-tag").strip()
    desc = request.form.get("description", "").strip()
    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for("admin.categories"))
    slug = slugify(name)
    if Category.query.filter_by(slug=slug).first():
        flash("A category with that name already exists.", "warning")
        return redirect(url_for("admin.categories"))
    cat = Category(name=name, slug=slug, icon=icon, description=desc)
    db.session.add(cat)
    db.session.commit()
    _log("create_category", "category", cat.id, name)
    flash(f'Category "{name}" created.', "success")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/categories/<int:cat_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    return jsonify({"active": cat.is_active})


@admin_bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.products:
        flash("Cannot delete a category that has listings.", "danger")
        return redirect(url_for("admin.categories"))
    db.session.delete(cat)
    db.session.commit()
    flash("Category deleted.", "info")
    return redirect(url_for("admin.categories"))


# ── Reviews moderation ────────────────────────────────────────────────────────

@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    page = request.args.get("page", 1, type=int)
    pagination = Review.query.order_by(Review.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/reviews.html", reviews=pagination.items, pagination=pagination, title="Manage Reviews")


@admin_bp.route("/reviews/<int:review_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = not review.is_approved
    db.session.flush()
    if review.reviewee.profile:
        review.reviewee.profile.recalculate_rating()
    db.session.commit()
    return jsonify({"approved": review.is_approved})


# ── Activity log ──────────────────────────────────────────────────────────────

@admin_bp.route("/logs")
@login_required
@admin_required
def logs():
    page = request.args.get("page", 1, type=int)
    pagination = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(page=page, per_page=30, error_out=False)
    return render_template("admin/logs.html", logs=pagination.items, pagination=pagination, title="Activity Log")

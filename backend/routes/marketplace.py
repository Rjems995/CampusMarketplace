"""routes/marketplace.py — Product CRUD, favorites, reports."""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify, current_app)
from flask_login import login_required, current_user

from backend.extensions import db
from backend.models.product import Product
from backend.models.product_image import ProductImage
from backend.models.category import Category
from backend.models.favorite import Favorite
from backend.models.report import Report
from backend.models.conversation import Conversation
from backend.forms.product_forms import ProductForm
from backend.forms.profile_forms import ReportForm, ReviewForm
from backend.utils.helpers import (save_image, delete_image, unique_slug,
                           create_notification)
from backend.middleware.decorators import not_suspended

marketplace_bp = Blueprint("marketplace", __name__, url_prefix="/marketplace")


# ── Browse by category ────────────────────────────────────────────────────────

@marketplace_bp.route("/category/<slug>")
def by_category(slug):
    cat  = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = (
        Product.query
        .filter_by(category_id=cat.id, status="available")
        .order_by(Product.created_at.desc())
        .paginate(page=page, per_page=current_app.config["LISTINGS_PER_PAGE"], error_out=False)
    )
    return render_template(
        "marketplace/category.html",
        category=cat,
        products=pagination.items,
        pagination=pagination,
        title=cat.name,
    )


# ── Product detail ────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<slug>")
def listing_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    product.increment_views()
    db.session.commit()

    is_favorited = False
    existing_conv = None
    if current_user.is_authenticated:
        is_favorited = bool(
            Favorite.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        )
        if current_user.id != product.seller_id:
            existing_conv = Conversation.query.filter_by(
                product_id=product.id, buyer_id=current_user.id
            ).first()

    related = (
        Product.query
        .filter_by(category_id=product.category_id, status="available")
        .filter(Product.id != product.id)
        .limit(4).all()
    )

    report_form = ReportForm()
    review_form = ReviewForm()

    return render_template(
        "marketplace/listing.html",
        product=product,
        is_favorited=is_favorited,
        existing_conv=existing_conv,
        related=related,
        report_form=report_form,
        review_form=review_form,
        title=product.title,
    )


# ── Create listing ────────────────────────────────────────────────────────────

@marketplace_bp.route("/create", methods=["GET", "POST"])
@login_required
@not_suspended
def create_listing():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.filter_by(is_active=True).order_by(Category.sort_order)
    ]

    if form.validate_on_submit():
        product = Product(
            seller_id=current_user.id,
            category_id=form.category_id.data,
            title=form.title.data.strip(),
            slug=unique_slug(form.title.data, Product),
            description=form.description.data.strip(),
            price=form.price.data,
            condition=form.condition.data,
            location=form.location.data.strip() if form.location.data else None,
        )
        db.session.add(product)
        db.session.flush()

        # Save uploaded images
        files = request.files.getlist("images")
        saved = 0
        for idx, f in enumerate(files):
            if f and f.filename:
                if saved >= current_app.config["MAX_PRODUCT_IMAGES"]:
                    break
                filename = save_image(f, "products", size=(800, 800))
                img = ProductImage(
                    product_id=product.id,
                    filename=filename,
                    is_primary=(idx == 0),
                    sort_order=idx,
                )
                db.session.add(img)
                saved += 1

        db.session.commit()
        flash("Listing created successfully!", "success")
        return redirect(url_for("marketplace.listing_detail", slug=product.slug))

    return render_template("marketplace/create_listing.html", form=form, title="Create Listing")


# ── Edit listing ──────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@not_suspended
def edit_listing(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.filter_by(is_active=True).order_by(Category.sort_order)
    ]

    if form.validate_on_submit():
        product.title       = form.title.data.strip()
        product.description = form.description.data.strip()
        product.price       = form.price.data
        product.condition   = form.condition.data
        product.category_id = form.category_id.data
        product.location    = form.location.data.strip() if form.location.data else None

        # Add new images
        files = request.files.getlist("images")
        current_count = len(product.images)
        for f in files:
            if f and f.filename and current_count < current_app.config["MAX_PRODUCT_IMAGES"]:
                filename = save_image(f, "products", size=(800, 800))
                img = ProductImage(
                    product_id=product.id,
                    filename=filename,
                    is_primary=(current_count == 0),
                    sort_order=current_count,
                )
                db.session.add(img)
                current_count += 1

        db.session.commit()
        flash("Listing updated!", "success")
        return redirect(url_for("marketplace.listing_detail", slug=product.slug))

    return render_template("marketplace/edit_listing.html", form=form, product=product, title="Edit Listing")


# ── Delete listing ────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_listing(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id and not current_user.is_admin:
        abort(403)

    for img in product.images:
        delete_image(img.filename, "products")

    db.session.delete(product)
    db.session.commit()
    flash("Listing deleted.", "info")
    return redirect(url_for("profile.my_listings"))


# ── Mark as sold ──────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/mark-sold", methods=["POST"])
@login_required
def mark_sold(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        abort(403)
    product.mark_sold()
    db.session.commit()
    flash("Listing marked as sold!", "success")
    return redirect(url_for("marketplace.listing_detail", slug=product.slug))


# ── Delete single image ───────────────────────────────────────────────────────

@marketplace_bp.route("/image/<int:image_id>/delete", methods=["POST"])
@login_required
def delete_image_route(image_id):
    img = ProductImage.query.get_or_404(image_id)
    if img.product.seller_id != current_user.id and not current_user.is_admin:
        abort(403)
    delete_image(img.filename, "products")
    was_primary = img.is_primary
    db.session.delete(img)
    if was_primary and img.product.images:
        remaining = [i for i in img.product.images if i.id != img.id]
        if remaining:
            remaining[0].is_primary = True
    db.session.commit()
    return jsonify({"ok": True})


# ── Toggle favorite ───────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    fav = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"favorited": False, "count": product.favorite_count})
    else:
        fav = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        # Notify seller
        if product.seller_id != current_user.id:
            create_notification(
                user_id=product.seller_id,
                ntype="favorite",
                title="Someone saved your listing",
                body=f'"{product.title}" was added to favorites.',
                link=url_for("marketplace.listing_detail", slug=product.slug),
            )
        return jsonify({"favorited": True, "count": product.favorite_count})


# ── Report listing ────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/report", methods=["POST"])
@login_required
def report_listing(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            product_id=product_id,
            reason=form.reason.data,
            description=form.description.data,
        )
        db.session.add(report)
        db.session.commit()
        flash("Report submitted. Our team will review it.", "info")
    return redirect(url_for("marketplace.listing_detail", slug=product.slug))


# ── Leave review ──────────────────────────────────────────────────────────────

@marketplace_bp.route("/listing/<int:product_id>/review", methods=["POST"])
@login_required
def leave_review(product_id):
    from backend.models.review import Review
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    if form.validate_on_submit():
        existing = Review.query.filter_by(reviewer_id=current_user.id, product_id=product_id).first()
        if existing:
            flash("You already reviewed this listing.", "warning")
        else:
            review = Review(
                reviewer_id=current_user.id,
                reviewee_id=product.seller_id,
                product_id=product_id,
                rating=form.rating.data,
                comment=form.comment.data,
            )
            db.session.add(review)
            db.session.flush()
            if product.seller.profile:
                product.seller.profile.recalculate_rating()
            db.session.commit()
            create_notification(
                user_id=product.seller_id,
                ntype="review",
                title="New review received",
                body=f"{current_user.full_name} left a {form.rating.data}★ review.",
                link=url_for("profile.view_profile", user_id=product.seller_id),
            )
            flash("Review submitted!", "success")
    return redirect(url_for("marketplace.listing_detail", slug=product.slug))

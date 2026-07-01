"""routes/main.py — Homepage, search, static pages."""

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_, func
from models.product import Product
from models.category import Category
from models.user import User
from extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured  = Product.query.filter_by(status="available", is_featured=True).order_by(Product.created_at.desc()).limit(6).all()
    newest    = Product.query.filter_by(status="available").order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    stats = {
        "total_listings": Product.query.filter_by(status="available").count(),
        "total_users":    User.query.count(),
        "total_sold":     Product.query.filter_by(status="sold").count(),
    }
    return render_template(
        "main/index.html",
        featured=featured,
        newest=newest,
        categories=categories,
        stats=stats,
        title="Campus Marketplace — Buy & Sell on Campus",
    )


@main_bp.route("/search")
def search():
    from flask import current_app
    q          = request.args.get("q", "").strip()
    category   = request.args.get("category", "")
    min_price  = request.args.get("min_price", type=float)
    max_price  = request.args.get("max_price", type=float)
    condition  = request.args.get("condition", "")
    location   = request.args.get("location", "").strip()
    sort       = request.args.get("sort", "newest")
    page       = request.args.get("page", 1, type=int)

    query = Product.query.filter_by(status="available")

    if q:
        query = query.filter(
            or_(
                Product.title.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%"),
            )
        )
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if condition:
        query = query.filter_by(condition=condition)
    if location:
        query = query.filter(Product.location.ilike(f"%{location}%"))

    # Sorting
    sort_map = {
        "newest":     Product.created_at.desc(),
        "oldest":     Product.created_at.asc(),
        "price_asc":  Product.price.asc(),
        "price_desc": Product.price.desc(),
        "popular":    Product.views.desc(),
    }
    query = query.order_by(sort_map.get(sort, Product.created_at.desc()))

    per_page   = current_app.config["LISTINGS_PER_PAGE"]
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()

    return render_template(
        "marketplace/search.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        q=q, category=category, condition=condition,
        min_price=min_price, max_price=max_price,
        location=location, sort=sort,
        title=f'Search: "{q}"' if q else "Browse Listings",
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html", title="About")

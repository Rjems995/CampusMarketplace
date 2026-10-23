"""
app.py — Application factory entry point.
Run with:  flask run   or   python app.py
"""

import os
from flask import Flask, render_template, request, url_for
from backend.config import get_config
from backend.extensions import db, bcrypt, login_manager, mail, csrf, migrate, socketio


def create_app(config_class=None):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__, template_folder=os.path.join(project_root, "frontend", "templates"),
                static_folder=os.path.join(project_root, "frontend", "static"),
                instance_path=os.path.join(project_root, "instance"))
    app.config.from_object(config_class or get_config())

    # ── Init extensions ───────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(
        app,
        async_mode=app.config.get("SOCKETIO_ASYNC_MODE", "gevent"),
        cors_allowed_origins=app.config.get("SOCKETIO_ALLOWED_ORIGINS"),
    )

    # ── Ensure upload dirs exist ──────────────────────────────────────────
    for subfolder in ("products", "avatars", "messages"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], subfolder), exist_ok=True)

    # ── Register blueprints ───────────────────────────────────────────────
    from backend.routes.main        import main_bp
    from backend.routes.auth        import auth_bp
    from backend.routes.marketplace import marketplace_bp
    from backend.routes.profile     import profile_bp
    from backend.routes.chat        import chat_bp
    from backend.routes.admin       import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    # ── Static file serving for uploads ──────────────────────────────────
    from flask import send_from_directory

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # ── Error handlers ────────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # ── Context processors ────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        from backend.models.category import Category
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
        from datetime import datetime
        def page_url(page):
            args = request.args.to_dict()
            args["page"] = page
            return url_for(request.endpoint, **dict(request.view_args or {}, **args))
        return {"categories": categories, "app_name": app.config["APP_NAME"],
                "current_year": datetime.now().year, "page_url": page_url}

    # ── Jinja2 filters ────────────────────────────────────────────────────
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"₱{float(value):,.2f}"
        except (TypeError, ValueError):
            return value

    @app.template_filter("time_ago")
    def time_ago_filter(dt):
        from datetime import datetime
        if not dt:
            return ""
        diff = datetime.utcnow() - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days < 7:
            return f"{days}d ago"
        return dt.strftime("%b %d, %Y")

    # ── CLI commands ──────────────────────────────────────────────────────
    from backend.commands import register_commands
    register_commands(app)

    return app

"""
app.py — Application factory entry point.
Run with:  flask run   or   python app.py
"""

import os
from flask import Flask, render_template
from config import get_config
from extensions import db, bcrypt, login_manager, mail, csrf, migrate, socketio


def create_app(config_class=None):
    app = Flask(__name__)
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
        cors_allowed_origins="*",
    )

    # ── Ensure upload dirs exist ──────────────────────────────────────────
    for subfolder in ("products", "avatars", "messages"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], subfolder), exist_ok=True)

    # ── Register blueprints ───────────────────────────────────────────────
    from routes.main        import main_bp
    from routes.auth        import auth_bp
    from routes.marketplace import marketplace_bp
    from routes.profile     import profile_bp
    from routes.chat        import chat_bp
    from routes.admin       import admin_bp

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
        from models.category import Category
        categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
        return {"categories": categories, "app_name": app.config["APP_NAME"]}

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
    from commands import register_commands
    register_commands(app)

    return app


# ── Run directly ──────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

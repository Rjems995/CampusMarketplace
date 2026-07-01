"""
commands.py — Custom Flask CLI commands.
Register with app.cli in the factory, or import in app.py.

Usage:
  flask seed-db         # Insert categories + admin user
  flask create-admin    # Create an admin interactively
  flask list-users      # Print all registered users
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from extensions import db


def register_commands(app):
    """Attach all CLI commands to the Flask app."""
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(list_users)
    app.cli.add_command(reset_db)


# ── seed-db ───────────────────────────────────────────────────────────────────

@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed the database with default categories and admin user."""
    from models.category import Category
    from models.user import User
    from models.profile import Profile

    db.create_all()
  
    # Categories
    default_categories = [
        ("Books",               "books",               "bi-book",             1),
        ("School Supplies",     "school-supplies",     "bi-pencil",           2),
        ("Electronics",         "electronics",         "bi-laptop",           3),
        ("Clothing",            "clothing",            "bi-bag",              4),
        ("Furniture",           "furniture",           "bi-house",            5),
        ("Sports",              "sports",              "bi-trophy",           6),
        ("Musical Instruments", "musical-instruments", "bi-music-note-beamed",7),
        ("Accessories",         "accessories",         "bi-watch",            8),
        ("Gaming",              "gaming",              "bi-controller",       9),
        ("Others",              "others",              "bi-three-dots",       10),
    ]
    added = 0
    for name, slug, icon, order in default_categories:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name=name, slug=slug, icon=icon, sort_order=order))
            added += 1
    db.session.commit()
    click.echo(f"✅ Added {added} categories (skipped existing).")

    # Admin user
    if not User.query.filter_by(email="admin@campus.edu").first():
        admin = User(
            email="admin@campus.edu",
            first_name="Campus",
            last_name="Admin",
            is_admin=True,
            email_confirmed=True,
            is_verified=True,
        )
        admin.set_password("Admin@1234")
        db.session.add(admin)
        db.session.flush()
        db.session.add(Profile(user_id=admin.id, school="Campus Marketplace HQ"))
        db.session.commit()
        click.echo("✅ Admin user created: admin@campus.edu / Admin@1234")
    else:
        click.echo("ℹ️  Admin user already exists, skipped.")


# ── create-admin ──────────────────────────────────────────────────────────────

@click.command("create-admin")
@click.option("--email",    prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--first",    prompt="First name")
@click.option("--last",     prompt="Last name")
@with_appcontext
def create_admin(email, password, first, last):
    """Interactively create a new admin user."""
    from models.user import User
    from models.profile import Profile

    if User.query.filter_by(email=email).first():
        click.echo(f"❌ A user with email {email} already exists.")
        return

    user = User(
        email=email.lower().strip(),
        first_name=first.strip(),
        last_name=last.strip(),
        is_admin=True,
        email_confirmed=True,
        is_verified=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(Profile(user_id=user.id))
    db.session.commit()
    click.echo(f"✅ Admin created: {user.full_name} <{user.email}>")


# ── list-users ────────────────────────────────────────────────────────────────

@click.command("list-users")
@with_appcontext
def list_users():
    """Print all registered users."""
    from models.user import User
    users = User.query.order_by(User.created_at).all()
    if not users:
        click.echo("No users found.")
        return
    click.echo(f"\n{'ID':<5} {'Email':<30} {'Name':<25} {'Admin':<6} {'Suspended'}")
    click.echo("-" * 75)
    for u in users:
        click.echo(f"{u.id:<5} {u.email:<30} {u.full_name:<25} {'Yes' if u.is_admin else 'No':<6} {'Yes' if u.is_suspended else 'No'}")
    click.echo(f"\nTotal: {len(users)} users\n")


# ── reset-db (DANGER) ─────────────────────────────────────────────────────────

@click.command("reset-db")
@click.option("--yes", is_flag=True, help="Confirm destructive reset.")
@with_appcontext
def reset_db(yes):
    """⚠️  DROP and recreate all tables (development only)."""
    if not yes:
        click.confirm("⚠️  This will DELETE all data. Continue?", abort=True)
    db.drop_all()
    db.create_all()
    click.echo("✅ Database reset complete. Run 'flask seed-db' to re-seed.")

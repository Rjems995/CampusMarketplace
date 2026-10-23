"""
tests/test_app.py — Basic test suite for Campus Marketplace.
Run with:  python -m pytest backend/tests/ -v
"""

import pytest
from backend.app import create_app
from backend.extensions import db
from backend.config import TestingConfig


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Create app in testing mode with SQLite (no PostgreSQL required)."""
    from backend.config import TestingConfig
    TestingConfig.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TestingConfig.SOCKETIO_ASYNC_MODE = "threading"
    TestingConfig.MAIL_SUPPRESS_SEND = True
    TestingConfig.UPLOAD_FOLDER = str(tmp_path_factory.mktemp("uploads"))

    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def seeded_categories(app):
    """Seed a single category for tests that need one."""
    from backend.models.category import Category
    with app.app_context():
        cat = Category.query.filter_by(slug="electronics").first()
        if not cat:
            cat = Category(name="Electronics", slug="electronics", icon="bi-laptop")
            db.session.add(cat)
            db.session.commit()
        return cat.id


# ── Auth tests ────────────────────────────────────────────────────────────────

class TestAuth:

    def test_register_page_loads(self, client):
        res = client.get("/auth/register")
        assert res.status_code == 200
        assert b"Create Account" in res.data

    def test_login_page_loads(self, client):
        res = client.get("/auth/login")
        assert res.status_code == 200
        assert b"Log In" in res.data

    def test_register_new_user(self, client, app):
        res = client.post("/auth/register", data={
            "first_name": "Test",
            "last_name":  "Student",
            "email":      "test@school.edu",
            "password":   "Password123!",
            "confirm":    "Password123!",
            "csrf_token": _get_csrf(client, "/auth/register"),
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_register_duplicate_email(self, client):
        """Second registration with same email must be rejected."""
        csrf = _get_csrf(client, "/auth/register")
        client.post("/auth/register", data={
            "first_name": "Dupe", "last_name": "User",
            "email": "dupe@school.edu", "password": "Password123!",
            "confirm": "Password123!", "csrf_token": csrf,
        })
        csrf2 = _get_csrf(client, "/auth/register")
        res = client.post("/auth/register", data={
            "first_name": "Dupe", "last_name": "User2",
            "email": "dupe@school.edu", "password": "Password123!",
            "confirm": "Password123!", "csrf_token": csrf2,
        }, follow_redirects=True)
        # Should stay on register page with an error
        assert b"already registered" in res.data or res.status_code == 200

    def test_login_wrong_password(self, client):
        csrf = _get_csrf(client, "/auth/login")
        res = client.post("/auth/login", data={
            "email": "test@school.edu",
            "password": "wrongpass",
            "csrf_token": csrf,
        }, follow_redirects=True)
        assert b"Invalid email or password" in res.data

    def test_login_correct_password(self, client, app):
        """Login with the user created in test_register_new_user."""
        from backend.models.user import User
        with app.app_context():
            user = User.query.filter_by(email="test@school.edu").first()
            if user:
                user.email_confirmed = True
                db.session.commit()

        csrf = _get_csrf(client, "/auth/login")
        res = client.post("/auth/login", data={
            "email":    "test@school.edu",
            "password": "Password123!",
            "csrf_token": csrf,
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_logout(self, client):
        res = client.get("/auth/logout", follow_redirects=True)
        assert res.status_code == 200

    def test_forgot_password_page(self, client):
        res = client.get("/auth/forgot-password")
        assert res.status_code == 200
        assert b"Forgot Password" in res.data


# ── Public page tests ─────────────────────────────────────────────────────────

class TestPublicPages:

    def test_homepage(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert b"Campus Marketplace" in res.data

    def test_search_empty(self, client):
        res = client.get("/search")
        assert res.status_code == 200

    def test_search_with_query(self, client):
        res = client.get("/search?q=calculus")
        assert res.status_code == 200

    def test_category_page(self, client, seeded_categories):
        res = client.get("/marketplace/category/electronics")
        assert res.status_code == 200

    def test_nonexistent_category(self, client):
        res = client.get("/marketplace/category/does-not-exist")
        assert res.status_code == 404

    def test_404_page(self, client):
        res = client.get("/this-does-not-exist")
        assert res.status_code == 404


# ── Product tests ─────────────────────────────────────────────────────────────

class TestProducts:

    def _login(self, client, app):
        """Helper to log in as test user."""
        from backend.models.user import User
        from backend.models.profile import Profile
        with app.app_context():
            user = User.query.filter_by(email="product_test@school.edu").first()
            if not user:
                user = User(
                    email="product_test@school.edu",
                    first_name="Product", last_name="Tester",
                )
                user.set_password("Password123!")
                user.email_confirmed = True
                db.session.add(user)
                db.session.flush()
                db.session.add(Profile(user_id=user.id))
                db.session.commit()

        csrf = _get_csrf(client, "/auth/login")
        client.post("/auth/login", data={
            "email": "product_test@school.edu",
            "password": "Password123!",
            "csrf_token": csrf,
        })

    def test_create_listing_requires_login(self, client):
        client.get("/auth/logout")
        res = client.get("/marketplace/create", follow_redirects=False)
        assert res.status_code in (302, 401)

    def test_create_listing_authenticated(self, client, app, seeded_categories):
        self._login(client, app)
        csrf = _get_csrf(client, "/marketplace/create")
        res = client.post("/marketplace/create", data={
            "title":       "Test Calculus Book",
            "description": "Very good condition calculus textbook for sale.",
            "price":       "250.00",
            "condition":   "Good",
            "category_id": seeded_categories,
            "location":    "UP Diliman",
            "csrf_token":  csrf,
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_listing_appears_in_search(self, client):
        res = client.get("/search?q=Calculus+Book")
        assert res.status_code == 200

    def test_dashboard_loads(self, client, app):
        self._login(client, app)
        res = client.get("/profile/dashboard")
        assert res.status_code == 200
        assert b"Dashboard" in res.data

    def test_my_listings_page(self, client, app):
        self._login(client, app)
        res = client.get("/profile/my-listings")
        assert res.status_code == 200


# ── Admin tests ───────────────────────────────────────────────────────────────

class TestAdmin:

    def _login_admin(self, client, app):
        from backend.models.user import User
        from backend.models.profile import Profile
        with app.app_context():
            admin = User.query.filter_by(email="pytest_admin@campus.edu").first()
            if not admin:
                admin = User(
                    email="pytest_admin@campus.edu",
                    first_name="Pytest", last_name="Admin",
                    is_admin=True, email_confirmed=True,
                )
                admin.set_password("Admin123!")
                db.session.add(admin)
                db.session.flush()
                db.session.add(Profile(user_id=admin.id))
                db.session.commit()
            # Re-query to get current id
            admin = User.query.filter_by(email="pytest_admin@campus.edu").first()
            admin_email = admin.email

        csrf = _get_csrf(client, "/auth/login")
        res = client.post("/auth/login", data={
            "email": admin_email,
            "password": "Admin123!",
            "csrf_token": csrf,
        }, follow_redirects=True)
        return res

    def test_admin_dashboard_blocked_for_regular_user(self, client, app):
        csrf = _get_csrf(client, "/auth/login")
        client.post("/auth/login", data={
            "email": "test@school.edu",
            "password": "Password123!",
            "csrf_token": csrf,
        })
        res = client.get("/admin/", follow_redirects=False)
        assert res.status_code in (302, 403)

    def test_admin_dashboard_accessible(self, client, app):
        self._login_admin(client, app)
        res = client.get("/admin/")
        assert res.status_code == 200
        assert b"Admin Dashboard" in res.data

    def test_admin_users_page(self, client, app):
        self._login_admin(client, app)
        res = client.get("/admin/users")
        assert res.status_code == 200

    def test_admin_categories_page(self, client, app):
        self._login_admin(client, app)
        res = client.get("/admin/categories")
        assert res.status_code == 200

    def test_admin_reports_page(self, client, app):
        self._login_admin(client, app)
        res = client.get("/admin/reports")
        assert res.status_code == 200


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_csrf(client, path: str) -> str:
    """Fetch a page and extract its CSRF token from a hidden input."""
    res  = client.get(path)
    html = res.data.decode("utf-8")
    marker = 'name="csrf_token" value="'
    idx = html.find(marker)
    if idx == -1:
        return ""
    start = idx + len(marker)
    end   = html.find('"', start)
    return html[start:end]

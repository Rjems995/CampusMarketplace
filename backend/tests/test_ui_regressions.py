"""Regression checks: python -m unittest backend.tests.test_ui_regressions -v."""
import tempfile
import unittest
from html import unescape
from pathlib import Path
from backend.app import create_app
from backend.config import TestingConfig
from backend.extensions import db
from backend.models.user import User
from backend.models.category import Category
from backend.models.product import Product
from backend.models.profile import Profile


class MarketplaceRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uploads = tempfile.TemporaryDirectory()
        class Config(TestingConfig):
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SOCKETIO_ASYNC_MODE = 'threading'
            MAIL_SUPPRESS_SEND = True
            UPLOAD_FOLDER = cls.uploads.name
        cls.app = create_app(Config)
        with cls.app.app_context():
            db.create_all()
            seller = User(email='seller@example.edu', first_name='Test', last_name='Seller', password_hash='unused')
            buyer = User(email='buyer@example.edu', first_name='Test', last_name='Buyer', password_hash='unused')
            category = Category(name='Books', slug='regression-books', icon='bi-book')
            db.session.add_all([seller, buyer, category])
            db.session.flush()
            db.session.add_all([Profile(user_id=seller.id), Profile(user_id=buyer.id)])
            cls.buyer_id = buyer.id
            for i in range(14):
                db.session.add(Product(seller_id=seller.id, category_id=category.id,
                    title=f'Regression book {i:02}', slug=f'regression-book-{i}',
                    description='A textbook for testing search pagination.', price=i,
                    condition='Good', location='Campus', status='available'))
            db.session.commit()
            cls.product_id = Product.query.first().id

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
        cls.uploads.cleanup()

    def setUp(self):
        self.client = self.app.test_client()

    def test_templates_and_assets_resolve_after_folder_split(self):
        self.assertEqual(Path(self.app.template_folder).parent.name, 'frontend')
        with self.app.app_context():
            for name in self.app.jinja_env.list_templates():
                self.app.jinja_env.get_template(name)
        for url in ['/', '/search', '/auth/login', '/auth/register', '/about',
                    '/marketplace/category/regression-books', '/marketplace/listing/regression-book-0',
                    '/static/css/main.css', '/static/js/main.js', '/static/images/no-image.png']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_first_page_links_preserve_query_filters_and_sort(self):
        url = '/search?q=Regression&category=regression-books&sort=price_asc&min_price=0'
        html = unescape(self.client.get(url).get_data(as_text=True))
        self.assertIn('page=2', html)
        self.assertIn('q=Regression&category=regression-books&sort=price_asc&min_price=0&page=2', html)
        self.assertIn('name="sort" value="price_asc"', html)
        second = self.client.get(url + '&page=2').get_data(as_text=True)
        self.assertIn('Regression book 13', second)
        self.assertNotIn('Regression book 00', second)

    def test_reversed_prices_and_invalid_numbers_are_handled(self):
        html = self.client.get('/search?q=Regression&min_price=5&max_price=2').get_data(as_text=True)
        self.assertIn('Regression book 02', html)
        self.assertIn('Regression book 05', html)
        self.assertNotIn('Regression book 06', html)
        for query in ['min_price=nan', 'max_price=inf', 'page=-1', 'page=bad', 'sort=unknown']:
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/search?' + query).status_code, 200)

    def test_empty_search_has_recovery_action(self):
        html = self.client.get('/search?q=no-such-listing').get_data(as_text=True)
        self.assertIn('No listings found', html)
        self.assertIn('Clear all filters', html)

    def test_save_toggle_persists_and_updates_accessible_state(self):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(self.buyer_id)
            session['_fresh'] = True
        url = f'/marketplace/listing/{self.product_id}/favorite'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['favorited'])
        self.assertIn('aria-pressed="true"', self.client.get('/search?sort=price_asc').get_data(as_text=True))
        self.assertFalse(self.client.post(url).get_json()['favorited'])

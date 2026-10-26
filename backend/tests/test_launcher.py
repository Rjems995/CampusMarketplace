"""Run with: python -m unittest backend.tests.test_launcher -v."""

from contextlib import redirect_stdout
from io import BytesIO, StringIO
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage

import run
from backend.extensions import db
from backend.local import create_local_app, prepare_database
from backend.models.category import Category
from backend.models.user import User
from backend.utils.helpers import save_image


class LocalSetupTests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        self.app = create_local_app(instance_dir=self.storage.name)
        self.addCleanup(self.close_database)

    def close_database(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_setup_is_repeatable_and_preserves_records(self):
        prepare_database(self.app)
        with self.app.app_context():
            category = Category.query.filter_by(slug="books").one()
            category.name = "My books"
            db.session.add(User(email="existing@example.edu", first_name="Existing",
                                last_name="Student", password_hash="unchanged"))
            db.session.commit()
        prepare_database(self.app)
        with self.app.app_context():
            self.assertEqual(Category.query.count(), 10)
            self.assertEqual(Category.query.filter_by(slug="books").one().name, "My books")
            self.assertEqual(User.query.one().password_hash, "unchanged")
        self.assertEqual(self.app.test_client().get("/").status_code, 200)

    def test_local_storage_and_session_secret_persist(self):
        second = create_local_app(instance_dir=self.storage.name, port=5051)
        self.assertEqual(second.secret_key, self.app.secret_key)
        self.assertTrue(second.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"))
        self.assertIn(Path(self.storage.name).as_posix(), second.config["SQLALCHEMY_DATABASE_URI"])
        self.assertEqual(second.config["FRONTEND_URL"], "http://localhost:5051")
        self.assertTrue(second.config["MAIL_SUPPRESS_SEND"])
        self.assertFalse(second.config["SESSION_COOKIE_SECURE"])

    def test_local_uploads_work_even_with_cloud_credentials(self):
        buffer = BytesIO()
        Image.new("RGB", (4, 4)).save(buffer, format="PNG")
        buffer.seek(0)
        credentials = {"CLOUDINARY_CLOUD_NAME": "configured-cloud",
                       "CLOUDINARY_API_KEY": "key", "CLOUDINARY_API_SECRET": "secret"}
        with self.app.app_context(), patch.dict(os.environ, credentials), \
                patch("backend.utils.helpers.cloudinary.uploader.upload") as upload:
            url = save_image(FileStorage(buffer, filename="image.png"), "products")
            upload.assert_not_called()
        self.assertTrue(url.startswith("/uploads/products/"))
        self.assertTrue((Path(self.app.config["UPLOAD_FOLDER"]) / "products" / url.rsplit("/", 1)[1]).is_file())
        with self.app.test_client().get(url) as response:
            self.assertEqual(response.status_code, 200)

    def test_configured_database_failure_has_readable_guidance(self):
        with patch("run.ensure_environment", return_value=None), \
                patch("backend.app.create_app", return_value=self.app), \
                patch("backend.local.prepare_database", side_effect=SQLAlchemyError("private connection details")), \
                redirect_stdout(StringIO()), self.assertRaises(run.StartupError) as error:
            run.main(["--configured", "--check"])
        self.assertIn("DATABASE_URL", str(error.exception))
        self.assertIn("without --configured", str(error.exception))
        self.assertNotIn("private connection details", str(error.exception))

    def test_manual_seed_command_still_creates_admin_once(self):
        runner = self.app.test_cli_runner()
        for _ in range(2):
            result = runner.invoke(args=["seed-db"])
            self.assertEqual(result.exit_code, 0, result.output)
        with self.app.app_context():
            self.assertEqual(Category.query.count(), 10)
            self.assertEqual(User.query.count(), 1)
            self.assertTrue(User.query.one().is_admin)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage.cleanup)
        root = Path(self.storage.name)
        self.requirements = root / "requirements.txt"
        self.requirements.write_text("Flask==3.0.3\n")
        self.stamp = root / "installed.sha256"
        patches = [patch.object(run, "REQUIREMENTS", (self.requirements,)),
                   patch.object(run, "STAMP", self.stamp),
                   patch("run.subprocess.run", return_value=subprocess.CompletedProcess([], 0))]
        self.install = patches[-1].start()
        self.addCleanup(patches[-1].stop)
        for item in patches[:-1]:
            item.start()
            self.addCleanup(item.stop)

    def test_install_once_then_reinstall_when_requirements_change(self):
        with redirect_stdout(StringIO()):
            run.ensure_dependencies()
            run.ensure_dependencies()
            self.assertEqual(self.install.call_count, 1)
            self.requirements.write_text("Flask==3.0.3\nPillow==10.3.0\n")
            run.ensure_dependencies()
            self.assertEqual(self.install.call_count, 2)

    def test_failed_install_is_retried_next_time(self):
        self.install.return_value.returncode = 1
        with redirect_stdout(StringIO()), self.assertRaises(run.StartupError):
            run.ensure_dependencies()
        self.assertFalse(self.stamp.exists())

    def test_force_install_runs_with_existing_stamp(self):
        self.stamp.write_text(run.dependency_fingerprint())
        with redirect_stdout(StringIO()):
            run.ensure_dependencies(force=True)
        self.install.assert_called_once()


if __name__ == "__main__":
    unittest.main()

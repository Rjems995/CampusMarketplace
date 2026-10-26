# Backend

This Python package owns the application factory, database models, HTTP routes,
Socket.IO handlers, validation, services, and tests. Use `backend.*` imports.

From the project root:

```powershell
.\run.cmd
```

This sets up Python dependencies and a persistent SQLite database automatically.
Use `--configured` to initialize and run against the database configured in `.env`.
Local startup code is in `local.py`; it seeds categories without adding an admin account.

For development and tests:

```sh
python -m pip install -r requirements-dev.txt
python -m unittest backend.tests.test_launcher -v
python -m unittest backend.tests.test_ui_regressions -v
python -m pytest backend/tests -v
python app.py
```

The application factory resolves `../frontend/templates`, `../frontend/static`,
`../instance`, and `../uploads` using absolute paths. The root `.env` is loaded
explicitly. Existing database and upload locations are preserved.

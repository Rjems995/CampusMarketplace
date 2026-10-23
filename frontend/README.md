# Frontend

Jinja templates live in `templates/`; CSS, browser JavaScript, and images live in `static/`.
Flask renders these files through `backend/app.py`. Start the application from the
project root with `python app.py`; no frontend build step is required.

Shared layout: `templates/base.html`. Homepage: `templates/main/index.html`.
Styles: `static/css/main.css`. Shared interactions: `static/js/main.js`.

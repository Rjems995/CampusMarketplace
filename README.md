# 🎓 Campus Marketplace

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue.svg)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-Realtime-black.svg)](https://socket.io/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media%20CDN-brightgreen.svg)](https://cloudinary.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, full-stack campus peer-to-peer web application built with **Flask 3**, **PostgreSQL**, **Flask-SocketIO**, and **Bootstrap 5**. Designed specifically for university students to buy, sell, and trade items—such as textbooks, school supplies, electronics, dorm furniture, and gear—safely within their verified academic community.

## Run from the terminal

Install **Python 3.12** once, then open PowerShell in the folder containing `run.cmd` and run:

```powershell
.\run.cmd
```

Open **http://localhost:5000**. Stop the server with **Ctrl+C**. Use the same command every time.

The first run creates `.venv`, installs dependencies, and creates the SQLite database and categories automatically. Internet access is needed for the first dependency installation. No virtual environment activation, PostgreSQL setup, `.env` editing, or frontend build is needed for this local mode.

Local accounts and listings persist in `instance/local.sqlite3`; photos are saved in `instance/uploads/`. Local mode disables outgoing email and Cloudinary uploads. Register an account in the app to get started. Existing PostgreSQL data is separate and is not copied into this local database.

If you are in the outer `CampusMarketplace` folder, enter the project folder first:

```powershell
cd .\CampusMarketplace
.\run.cmd
```

Optional commands:

```powershell
.\run.cmd --port 5001    # Choose another port
.\run.cmd --check        # Set up and check the app without starting the server
.\run.cmd --install      # Run dependency installation again
.\run.cmd --configured   # Use the database and services configured in .env
```

`--configured` requires the configured database to exist and its server to be running. It creates missing tables and categories, and preserves existing records. It does not create an admin account. The manual `flask seed-db` command below creates the documented default admin.

On macOS/Linux, run `python3.12 run.py`. On Windows you can also use `py -3.12 run.py`. If Python 3.12 is missing, install it with `py install 3.12`, then reopen the terminal.

---

## 📸 Application Preview

<div align="center">

### 🏠 Search-First Homepage
*Real-time student marketplace statistics, category carousel, and featured campus listings.*
<br/>
<img src="docs/screenshots/01_homepage.png" alt="Campus Marketplace Homepage" width="900" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />

<br/><br/>

### 🔍 Catalog Search & Multi-Filter Engine
*Filter by category, price range, condition, and campus pickup location with persistent sorting and pagination.*
<br/>
<img src="docs/screenshots/02_browse_search.png" alt="Catalog Search and Filters" width="900" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />

<br/><br/>

### 📦 Product Listing Detail & Inquiry
*Interactive image gallery, condition badges, seller ratings, and direct 1-on-1 messaging.*
<br/>
<img src="docs/screenshots/03_listing_detail.png" alt="Listing Detail View" width="900" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />

</div>

<br/>

<details>
<summary><b>👀 Click to view Authentication & Information Pages</b></summary>
<br/>

| Student Login | University Domain Registration |
| :---: | :---: |
| <img src="docs/screenshots/04_auth_login.png" alt="Student Login" width="450" /> | <img src="docs/screenshots/05_auth_register.png" alt="Student Registration" width="450" /> |

<br/>

| About & Campus Guidelines |
| :---: |
| <img src="docs/screenshots/06_about.png" alt="About and Guidelines" width="700" /> |

</details>

---

## 📑 Table of Contents

- [Run from the terminal](#run-from-the-terminal)
- [📸 Application Preview](#-application-preview)
- [✨ Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Architecture](#-project-architecture)
- [🚀 Quickstart & Installation](#-quickstart--installation)
  - [1. Clone Repository](#1-clone-the-repository)
  - [2. Virtual Environment Setup](#2-create-and-activate-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Database Initialization & Seeding](#5-database-initialization--seeding)
  - [6. Generate Asset Placeholders](#6-generate-placeholder-assets)
  - [7. Run the Application](#7-run-the-application)
- [👤 Default Admin Account](#-default-admin-account)
- [💻 Custom Flask CLI Commands](#-custom-flask-cli-commands)
- [🧪 Testing & UI Verification](#-testing--ui-verification)
- [☁️ Cloudinary Media Setup](#️-cloudinary-media-setup)
- [📧 Email Setup (Gmail SMTP)](#-email-setup-gmail-smtp)
- [🔐 Security Highlights](#-security-highlights)
- [🌐 Production Deployment](#-production-deployment)
- [📄 License](#-license)

---

## ✨ Features

| Module | Features & Capabilities |
| :--- | :--- |
| **Authentication & Access** | • Domain-restricted registration (e.g. `@up.edu.ph`)<br>• Email confirmation workflow & password reset tokens<br>• Secure password hashing via `Flask-Bcrypt`<br>• "Remember Me" persistent sessions<br>• Role-based authorization (`admin_required`, `verified_required`)<br>• Instant account suspension check at session verification level |
| **Marketplace & Listings** | • Create, edit, and delete product listings<br>• Multi-image photo gallery (up to 6 photos) hosted via **Cloudinary CDN**<br>• Image auto-resizing & optimization using Pillow<br>• Mark items as *Available* or *Sold*<br>• Sold listings showcase on public seller profiles<br>• View counters and category browsing |
| **Search & Discovery** | • Search-first homepage with real-time community listing statistics<br>• Full-text keyword search across item titles and descriptions<br>• Multi-criteria filtering (category, price range, item condition, location)<br>• Sorting (Newest, Oldest, Price Low-High, Price High-Low, Most Popular)<br>• URL query preservation across paginated browsing |
| **Real-Time Chat** | • 1-on-1 buyer-seller messaging powered by **Flask-SocketIO**<br>• Real-time typing indicators and live read receipts<br>• Online / offline / last-seen user status tracking<br>• In-chat image sharing & attachments<br>• Unread message counter badges and transactional email alerts |
| **Favorites & Watchlist** | • Asynchronous save/favorite button with visual feedback<br>• Dedicated user Favorites collection view |
| **Notifications** | • In-app notification center for buyer inquiries, reviews, and status changes<br>• Live WebSocket notifications pushed directly to active browser sessions |
| **Reviews & Ratings** | • 1-to-5 star rating system with written feedback<br>• Automatic recalculation of seller average rating and review counts on profile |
| **Reports & Moderation** | • User report submissions on suspect listings with predefined reason categories<br>• Admin moderation dashboard to review, resolve, or dismiss reports |
| **Administration** | • Centralized admin dashboard with user metrics and platform activity logs<br>• User management: promote to admin, suspend/unsuspend, or permanently delete<br>• Category CRUD management with custom icons and sort ordering<br>• Direct listing removal and review moderation |
| **Design & Accessibility** | • Clean, modern UI built on **Bootstrap 5** and custom CSS design tokens<br>• **Dark / Light theme toggle** with local storage persistence and system preference detection<br>• Responsive mobile, tablet, and desktop layouts<br>• Accessibility compliance (`aria-labels`, high-contrast states, reduced-motion query support)<br>• Custom branded error pages (403, 404, 500) |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, Flask 3.0.3, Flask-Login, Flask-SocketIO, Flask-WTF, Flask-Mail, Flask-Migrate, Flask-Bcrypt, SQLAlchemy ORM, Bleach
- **Database:** SQLite (local launcher and tests), PostgreSQL 14+ (configured environments and production)
- **Frontend:** Jinja2 server-rendered templates, Vanilla ES6+ JavaScript, Bootstrap 5.3, Bootstrap Icons *(No Node.js or Webpack build step required)*
- **Real-Time:** WebSockets / Long-polling via Socket.IO (`threading` for development, `gevent` for production)
- **Cloud Media Storage:** [Cloudinary](https://cloudinary.com/) (persistent cloud hosting & CDN delivery for avatars, product photos, and chat attachments) + [Pillow](https://python-pillow.org/) (server-side image validation, compression, and resizing) with automatic local storage fallback
- **Testing:** pytest, unittest, in-memory SQLite fixtures

---

## 📁 Project Architecture

The codebase follows a decoupled modular structure where frontend presentation assets and backend application logic are cleanly organized:

```
CampusMarketplace/
├── app.py                      # Root launcher (Socket.IO + Flask application)
├── run.cmd                     # One-command Windows setup and startup
├── run.py                      # Environment setup and local/configured startup
├── build.sh                    # Deployment build script (installs packages + seeds DB)
├── requirements.txt            # Production dependencies (points to backend/requirements.txt)
├── requirements-dev.txt        # Development dependencies (includes pytest)
├── .env.example                # Template for environment configuration
│
├── docs/                       # Project documentation assets
│   └── screenshots/            # UI screenshots previewed in README
│
├── frontend/                   # ── Presentation Layer ──────────────────
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Master layout with responsive navbar, dark mode, & footer
│   │   ├── admin/              # Admin dashboard, users, listings, categories, reports, logs
│   │   ├── auth/               # Login, register, email verification, password reset
│   │   ├── chat/               # Real-time inbox and conversation rooms
│   │   ├── errors/             # Custom 403, 404, 500 error pages
│   │   ├── main/               # Search-first homepage, about page
│   │   ├── marketplace/        # Catalog, listing details, create/edit forms, product cards
│   │   └── profile/            # User profile, edit profile, my listings, favorites, notifications
│   └── static/                 # Static web assets
│       ├── css/main.css        # Custom CSS variables, dark/light theme, component styles
│       ├── js/main.js          # Client-side scripts (Socket.IO, dark mode, toasts, favorites)
│       └── images/             # Placeholders, icons, brand assets
│
├── backend/                    # ── Application Layer ───────────────────
│   ├── app.py                  # Flask application factory (create_app)
│   ├── config.py               # Environment configuration (Dev, Test, Prod)
│   ├── extensions.py           # Initialized Flask extensions (db, socketio, bcrypt, mail, csrf)
│   ├── commands.py             # Custom Flask CLI commands (seed-db, create-admin, list-users)
│   ├── database/               # SQL database schema and seed data files
│   │   ├── schema.sql          # PostgreSQL DDL table definitions & indexes
│   │   └── seed.sql            # Initial category catalog and default admin
│   ├── forms/                  # WTForms form classes & input validation
│   ├── middleware/             # Route security decorators (admin_required, verified_required)
│   ├── models/                 # SQLAlchemy models (User, Product, Conversation, etc.)
│   ├── routes/                 # Blueprint controllers (main, auth, marketplace, chat, admin)
│   ├── services/               # Transactional email dispatcher (email_service.py)
│   ├── utils/                  # Helpers (Cloudinary uploads, image processing, slugs, tokens)
│   └── tests/                  # Automated test suite (test_app.py, test_ui_regressions.py)
│
├── instance/                   # Local database storage & runtime files (gitignored)
└── uploads/                    # Local temporary/fallback upload directory (gitignored)
```

---

## 🚀 Quickstart & Installation

For the easiest local setup, use [Run from the terminal](#run-from-the-terminal) above. The following steps are for manually configuring PostgreSQL and external services.

### 1. Clone the repository

```bash
git clone https://github.com/yourname/campus-marketplace.git
cd campus-marketplace
```

### 2. Create and activate virtual environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

### 3. Install dependencies

For standard application run:
```bash
pip install -r requirements.txt
```

For development (includes test runner `pytest`):
```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Open `.env` and configure your settings:

```ini
# Flask Core
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change-to-a-secure-random-secret-key
APP_NAME="Campus Marketplace"
FRONTEND_URL=http://localhost:5000

# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/campus_marketplace

# University Email Domain (Only emails ending with this domain can register)
SCHOOL_EMAIL_DOMAIN=@up.edu.ph

# Real-Time (Socket.IO)
SOCKETIO_ASYNC_MODE=threading

# Media Storage (Cloudinary - optional; automatically falls back to local storage if unconfigured)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email Delivery (Optional for local testing, required for verification & notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER="Campus Marketplace <your_email@gmail.com>"
```

### 5. Database Initialization & Seeding

Ensure your PostgreSQL service is running and create the database:
```bash
psql -U postgres -c "CREATE DATABASE campus_marketplace;"
```

#### Option A: Using the built-in Flask CLI (Recommended)
The built-in command initializes the tables using SQLAlchemy models and seeds default categories and an admin account:
```bash
flask seed-db
```

#### Option B: Using raw SQL scripts
Alternatively, run the SQL schema and seed files directly:
```bash
psql -U postgres -d campus_marketplace -f backend/database/schema.sql
psql -U postgres -d campus_marketplace -f backend/database/seed.sql
```

### 6. Generate placeholder assets

Generate default avatar and product placeholder images:
```bash
python -m backend.utils.create_placeholders
```

### 7. Run the application

Start the server using `app.py` (which launches Flask with Socket.IO support):
```bash
python app.py
```

*Or via Flask CLI:*
```bash
flask run
```

Open your browser and navigate to **http://localhost:5000** 🎉

---

## 👤 Default Admin Account

The manual `flask seed-db` command creates a default administrative account. The local `run.cmd` launcher only seeds categories; register a regular account to try the app.

| Attribute | Credential |
| :--- | :--- |
| **Email** | `admin@campus.edu` |
| **Password** | `Admin@1234` |
| **Role** | System Administrator (`is_admin = True`) |

> ⚠️ **Important:** Change the default admin password immediately after logging in for production or shared environments.

---

## 💻 Custom Flask CLI Commands

Campus Marketplace includes custom Flask CLI commands registered in `backend/commands.py`:

```bash
# Seed database with default categories and initial admin user
flask seed-db

# Interactively create a new administrative user with custom details
flask create-admin

# Print a formatted table of all registered users, roles, and suspension statuses
flask list-users

# DANGER: Drop and recreate all tables (Development use only)
flask reset-db --yes
```

---

## 🧪 Testing & UI Verification

The automated test suite runs against an isolated **in-memory SQLite** database with suppressed email delivery and temporary upload directories. No running PostgreSQL or Cloudinary service is required to run tests.

### Running the test suite:

```bash
# Run all unit and integration tests (Auth, Marketplace, Chat, Admin, Models)
python -m pytest backend/tests -v

# Run UI regression tests (Pagination, Filter retention, Product cards, Theme states)
python -m unittest backend.tests.test_ui_regressions -v
```

### What the test suite covers:
- **Authentication & Security:** Registration validation, school email domain restrictions, duplicate email rejection, invalid logins, and session persistence.
- **Marketplace Workflows:** Listing creation, price formatting, condition filtering, status toggling (available vs. sold), and seller authorization checks.
- **UI Regressions:** Search query preservation across pagination, filter-combination stability, category views, and responsive component rendering.
- **Permissions:** Admin route protection and unauthorized access redirects (`403 Forbidden`).

---

## ☁️ Cloudinary Media Setup

Campus Marketplace supports both cloud storage via [Cloudinary](https://cloudinary.com/) and local disk storage:
1. Uploaded images are checked for allowed extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`).
2. Images are preprocessed and optimized via Pillow (aspect-ratio preservation and LANCZOS compression).
3. If Cloudinary credentials are provided, the image is uploaded directly to your Cloudinary storage under organized subfolders (`products/`, `avatars/`, `messages/`).
4. If Cloudinary is not configured or encounters network issues, the application **automatically falls back to local file storage** under `uploads/`, ensuring seamless operation in any environment.

To configure Cloudinary:
1. Sign up for a free account at [Cloudinary](https://cloudinary.com/).
2. Locate your **Cloud Name**, **API Key**, and **API Secret** on your Cloudinary dashboard.
3. Paste these values into your `.env` file under `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.

---

## 📧 Email Setup (Gmail SMTP)

To enable email verification, password reset links, and new message notification emails:

1. Enable **2-Step Verification** on your Google Account:
   - Go to [Google Account Security](https://myaccount.google.com/security).
2. Generate an **App Password**:
   - Navigate to **2-Step Verification** → **App passwords**.
   - Create an app named "Campus Marketplace".
3. Copy the 16-character generated password and place it in `.env`:
   ```ini
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_gmail_address@gmail.com
   MAIL_PASSWORD=your_16_character_app_password
   MAIL_DEFAULT_SENDER="Campus Marketplace <your_gmail_address@gmail.com>"
   ```

*(Note: During tests, email delivery is automatically mocked and suppressed).*

---

## 🔐 Security Highlights

- [x] **Password Protection:** Industry-standard bcrypt password hashing (never stored in plain text).
- [x] **CSRF Protection:** Flask-WTF CSRF tokens validated on all mutating HTTP POST/PUT/DELETE requests.
- [x] **SQL Injection Defense:** Strict usage of SQLAlchemy ORM parameterized queries.
- [x] **XSS Mitigation:** Automatic HTML escaping in Jinja2 templates and Bleach sanitization.
- [x] **Cookie Hardening:** `HttpOnly`, `SameSite=Lax`, and configurable `SESSION_COOKIE_SECURE` for HTTPS production environments.
- [x] **Access Control:** Route-level decorators (`@login_required`, `@admin_required`, `@verified_required`).
- [x] **Image Sanitization:** File extension validation, MIME type checks, and Pillow re-encoding to strip malicious embedded payloads.
- [x] **Account Suspension:** Suspended users are immediately blocked from logging in or continuing active sessions.

---

## 🌐 Production Deployment

### Deployment on PaaS (Render, Railway, Fly.io, Heroku)

A preconfigured `build.sh` script is provided for automatic build and database migration:

```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python -m flask seed-db
```

1. **Build Command:** `./build.sh`
2. **Start Command:**
   ```bash
   gunicorn -k gevent -w 1 "app:app"
   ```
3. **Environment Variables:** Set all `.env` variables in your platform dashboard (including `FLASK_ENV=production`, `SESSION_COOKIE_SECURE=True`, and `DATABASE_URL`).
4. **Persistent Media:** Cloudinary handles media persistence automatically, eliminating data loss from ephemeral server containers.

### Self-Hosted Linux VPS (Ubuntu / Debian + Nginx)

1. Set up a systemd service pointing to Gunicorn with Gevent workers:
   ```ini
   [Unit]
   Description=Gunicorn instance to serve Campus Marketplace
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/CampusMarketplace
   Environment="PATH=/var/www/CampusMarketplace/.venv/bin"
   ExecStart=/var/www/CampusMarketplace/.venv/bin/gunicorn --worker-class gevent -w 2 --bind 127.0.0.1:5000 "app:app"

   [Install]
   WantedBy=multi-user.target
   ```
2. Configure **Nginx** reverse proxy for SSL termination and static caching.

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute for educational, portfolio, and commercial purposes.

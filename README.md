# 🎓 Campus Marketplace

A full-stack student marketplace web application built with **Flask + PostgreSQL**.  
Students can buy, sell, and trade items safely within their university community.

---

## ✨ Features

| Area | What's included |
|------|----------------|
| **Auth** | Register, Login, Logout, Remember Me, Email Verification, Forgot/Reset Password, Password Hashing (bcrypt) |
| **Marketplace** | Create/Edit/Delete listings, Image gallery (up to 6 photos), Mark as Sold, Category browsing, Featured listings |
| **Search** | Full-text search, Filter by category, price, condition, location, sort options |
| **Messaging** | Real-time chat (Flask-SocketIO), Typing indicator, Online status, Image sharing, Unread badge |
| **Favorites** | Save/remove listings, Favorites page |
| **Notifications** | In-app + real-time push via SocketIO |
| **Reviews** | Star ratings, Comments, Average rating on seller profile |
| **Reports** | Report listings with reason, Admin review workflow |
| **Admin** | User management (suspend/delete/promote), Listing moderation, Category CRUD, Report review, Activity log |
| **UI/UX** | Bootstrap 5, Dark/Light mode, Responsive, Toast notifications, Loading states, Empty states |

---

## 🛠 Tech Stack

- **Backend:** Python 3.11+, Flask 3, Flask-Login, Flask-SocketIO, Flask-Mail, Flask-Migrate
- **Database:** PostgreSQL 14+ with SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Vanilla JS, Bootstrap 5, Bootstrap Icons
- **Real-time:** Socket.IO (gevent)
- **Images:** Pillow (auto-resize + compress)

---

## 🚀 Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourname/campus-marketplace.git
cd campus-marketplace
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your values
```

Key `.env` values to set:
```
SECRET_KEY=your-random-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/campus_marketplace
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-gmail-app-password
SCHOOL_EMAIL_DOMAIN=@your.edu.ph
```

### 5. Set up PostgreSQL database
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE campus_marketplace;"

# Apply schema
psql -U postgres -d campus_marketplace -f database/schema.sql

# Seed categories and admin user
psql -U postgres -d campus_marketplace -f database/seed.sql
```

### 6. Generate placeholder images
```bash
python utils/create_placeholders.py
```

### 7. Run the application
```bash
python app.py
# or
flask run
```

Open **http://localhost:5000**

---

## 👤 Default Admin Account

| Field | Value |
|-------|-------|
| Email | `admin@campus.edu` |
| Password | `Admin@1234` |

> ⚠️ Change the password immediately after first login.

---

## 📁 Project Structure

```
CampusMarketplace/
├── app.py                  # Application factory & entry point
├── config.py               # Environment-based configuration
├── extensions.py           # Flask extension instances
├── requirements.txt
├── .env.example
│
├── database/
│   ├── schema.sql          # Full PostgreSQL schema
│   └── seed.sql            # Categories + admin user
│
├── models/                 # SQLAlchemy models (one per file)
│   ├── user.py
│   ├── profile.py
│   ├── product.py
│   ├── category.py
│   ├── conversation.py     # + Message
│   ├── review.py
│   ├── notification.py
│   ├── report.py
│   ├── admin_log.py
│   └── token.py            # EmailVerification + PasswordReset
│
├── routes/                 # Blueprint route handlers
│   ├── main.py             # Homepage, search
│   ├── auth.py             # Login, register, password
│   ├── marketplace.py      # Listings CRUD, favorites, reports
│   ├── profile.py          # Dashboard, profile, notifications
│   ├── chat.py             # Messaging + SocketIO events
│   └── admin.py            # Admin panel
│
├── forms/                  # WTForms
│   ├── auth_forms.py
│   ├── product_forms.py
│   └── profile_forms.py
│
├── services/
│   └── email_service.py    # Transactional email templates
│
├── utils/
│   ├── helpers.py          # Image utils, slug, tokens, notifications
│   └── create_placeholders.py
│
├── middleware/
│   └── decorators.py       # admin_required, verified_required
│
├── templates/
│   ├── base.html           # Master layout with navbar + footer
│   ├── main/               # Homepage, about
│   ├── auth/               # Login, register, password pages
│   ├── marketplace/        # Listings, search, category
│   ├── profile/            # Dashboard, profile, settings
│   ├── chat/               # Inbox, conversation
│   ├── admin/              # Admin dashboard + management pages
│   └── errors/             # 403, 404, 500
│
├── static/
│   ├── css/main.css        # Custom styles + design tokens
│   ├── js/main.js          # Dark mode, toasts, SocketIO, favorites
│   └── images/             # Placeholder images
│
└── uploads/                # User-uploaded files (gitignored)
    ├── products/
    ├── avatars/
    └── messages/
```

---

## 🔐 Security Checklist

- [x] Passwords hashed with bcrypt (never stored plain text)
- [x] CSRF protection on all forms (Flask-WTF)
- [x] SQL injection prevention via SQLAlchemy ORM
- [x] XSS prevention via Jinja2 auto-escaping
- [x] Secure session cookies (HttpOnly, SameSite=Lax)
- [x] Role-based access control (admin_required decorator)
- [x] File upload validation (extension + Pillow re-encode)
- [x] Suspended user login blocked at Flask-Login level
- [x] Admin can only be created by another admin

---

## 📧 Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a password for "Mail"
4. Use it as `MAIL_PASSWORD` in `.env`

---

## 🌐 Deployment (Production)

1. Set `FLASK_ENV=production` and `SESSION_COOKIE_SECURE=True`
2. Use a WSGI server: `gunicorn -k gevent -w 1 "app:app"`
3. Put Nginx in front for static files and SSL termination
4. Use environment variables (not `.env` files) on the server
5. Run `flask db upgrade` for migrations

---

## 📄 License

MIT — free to use for educational and portfolio purposes.

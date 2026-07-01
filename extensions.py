"""
extensions.py — Flask extension instances.
Import from here everywhere to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_socketio import SocketIO

db       = SQLAlchemy()
bcrypt   = Bcrypt()
login_manager = LoginManager()
mail     = Mail()
csrf     = CSRFProtect()
migrate  = Migrate()
socketio = SocketIO()

# Flask-Login settings
login_manager.login_view       = "auth.login"
login_manager.login_message    = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id: str):
    from models.user import User
    return User.query.get(int(user_id))

"""Compatibility launcher. Run from the project root: python app.py."""
from backend.app import create_app
from backend.extensions import socketio

app = create_app()

if __name__ == "__main__":
    debug = app.config.get("DEBUG", False)
    socketio.run(app, debug=debug, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

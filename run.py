"""Set up and run the local app: run.cmd (Windows) or python3.12 run.py."""

import argparse
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import venv


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
REQUIREMENTS = (ROOT / "requirements.txt", ROOT / "backend/requirements.txt")
STAMP = VENV / ".campus-requirements.sha256"


class StartupError(Exception):
    """An actionable setup problem that does not need a traceback."""


def dependency_fingerprint():
    digest = hashlib.sha256(sys.version.encode())
    for requirements in REQUIREMENTS:
        digest.update(requirements.read_bytes())
    return digest.hexdigest()


def environment_is_usable():
    if not VENV_PYTHON.is_file():
        return False
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", "import sys; sys.exit(sys.version_info[:2] != (3, 12))"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def ensure_dependencies(force=False):
    fingerprint = dependency_fingerprint()
    if not force and STAMP.is_file() and STAMP.read_text().strip() == fingerprint:
        return
    print("Installing application dependencies (first run or requirements changed)...", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
         "-r", str(REQUIREMENTS[0])], cwd=ROOT, check=False,
    )
    if result.returncode:
        raise StartupError("Dependency installation failed. Check your internet connection and run again.")
    STAMP.write_text(fingerprint, encoding="utf-8")


def ensure_environment(args):
    if sys.version_info[:2] != (3, 12):
        raise StartupError("Use Python 3.12: run .\\run.cmd on Windows, or python3.12 run.py.")
    # Compare environment prefixes; resolving executable symlinks alone is insufficient on Unix.
    if Path(sys.prefix).resolve() != VENV.resolve():
        if not environment_is_usable():
            print("Creating the project's Python environment...", flush=True)
            venv.EnvBuilder(with_pip=True).create(VENV)
        return subprocess.call([str(VENV_PYTHON), str(ROOT / "run.py"), *args], cwd=ROOT)
    ensure_dependencies(force="--install" in args)
    return None


def available_port(value):
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main(argv=None):
    parser = argparse.ArgumentParser(description="Set up and start Campus Marketplace locally.")
    parser.add_argument("--configured", action="store_true", help="Use the database and services from .env.")
    parser.add_argument("--port", type=available_port, default=5000, help="Local port (default: 5000).")
    parser.add_argument("--check", action="store_true", help="Set up and check the app without starting a server.")
    parser.add_argument("--install", action="store_true", help="Run dependency installation again.")
    args_list = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(args_list)

    child_result = ensure_environment(args_list)
    if child_result is not None:
        return child_result

    from backend.local import create_local_app, prepare_database
    from backend.extensions import socketio
    from sqlalchemy.exc import SQLAlchemyError

    try:
        if args.configured:
            from backend.app import create_app
            app = create_app()
            print("Using the database and services configured in .env.", flush=True)
        else:
            app = create_local_app(port=args.port)
            print(f"Local database: {ROOT / 'instance' / 'local.sqlite3'}", flush=True)
            print("Local uploads enabled. Outgoing email disabled. Use --configured for your .env services.", flush=True)
        prepare_database(app)
    except SQLAlchemyError:
        if args.configured:
            raise StartupError(
                "Could not initialize the configured database. Check DATABASE_URL in .env, "
                "start PostgreSQL, and make sure the database exists. "
                "Run without --configured to use local SQLite."
            ) from None
        raise StartupError("Could not initialize instance/local.sqlite3. Check folder permissions and free disk space.") from None

    if args.check:
        with app.test_client() as client:
            response = client.get("/")
            if response.status_code != 200:
                raise StartupError("The homepage check failed. See the application log above.")
        print("Setup complete. Database and homepage checks passed.", flush=True)
        return 0

    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", args.port))
    except OSError:
        raise StartupError(f"Port {args.port} is unavailable. Try: .\\run.cmd --port {args.port + 1 if args.port < 65535 else 5000}") from None

    print(f"\nOpen http://localhost:{args.port}  |  Press Ctrl+C to stop.\n", flush=True)
    socketio.run(app, host="127.0.0.1", port=args.port, debug=False,
                 use_reloader=False, allow_unsafe_werkzeug=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
    except (StartupError, OSError, subprocess.SubprocessError) as exc:
        print(f"\nStartup failed: {exc}", file=sys.stderr)
        sys.exit(1)

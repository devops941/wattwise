"""
WattWise Application Entrypoint Runner
Automatically selects an available local port and bootstraps Streamlit cleanly.
Auto-detects and activates the project virtual environment (venv) if not already active.
"""
import os
import sys
import socket
import subprocess
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent)
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")

# 1. AUTO-VENV BOOTSTRAPPER:
# If user runs 'python run_app.py' without activating the virtual environment,
# automatically relaunch using the project's virtualenv Python interpreter.
try:
    import streamlit
except ImportError:
    if os.path.exists(VENV_PYTHON) and os.path.abspath(sys.executable).lower() != os.path.abspath(VENV_PYTHON).lower():
        # Relaunch script seamlessly using venv python
        completed = subprocess.run([VENV_PYTHON] + sys.argv)
        sys.exit(completed.returncode)
    else:
        print("\n❌ Error: Streamlit is not installed in this Python environment.")
        print(f"👉 Please activate the project venv: .\\venv\\Scripts\\Activate.ps1\n")
        sys.exit(1)

# Set clean environment defaults
os.environ["USERPROFILE"] = BASE_DIR
os.environ["HOME"] = BASE_DIR
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"


def is_port_in_use(port: int) -> bool:
    """Checks whether a port is currently occupied or restricted on any interface."""
    # Check 1: Active listener probe
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
    except Exception:
        pass

    # Check 2: Exclusive bind probe on all interfaces (Windows-safe)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            s.bind(("0.0.0.0", port))
            return False
    except OSError:
        return True


def find_available_port(start_port: int = 8501, max_tries: int = 30) -> int:
    """Finds the first actually available TCP port."""
    for port in range(start_port, start_port + max_tries):
        if not is_port_in_use(port):
            return port
    return start_port


from streamlit.web.cli import main

if __name__ == "__main__":
    app_path = os.path.join(BASE_DIR, "app.py")

    # Check if user specified an explicit custom port
    custom_port = None
    for i, arg in enumerate(sys.argv):
        if arg in ("--port", "--server.port") and i + 1 < len(sys.argv):
            custom_port = sys.argv[i + 1]
            break
        elif arg.startswith("--server.port="):
            custom_port = arg.split("=")[1]
            break

    if not custom_port:
        port = find_available_port(8501)
        if port != 8501:
            print("\n" + "=" * 60)
            print(f"⚠️  Note: Port 8501 is currently occupied by another process.")
            print(f"⚡ Automatically routed WattWise to available port: {port}")
            print(f"👉 Local URL: http://localhost:{port}")
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print(f"⚡ Starting WattWise Household Energy Intelligence")
            print(f"📍 Local Port: {port}")
            print(f"👉 Local URL: http://localhost:{port}")
            print("=" * 60 + "\n")

        # Strip any extraneous args and launch on selected free port
        filtered_args = [a for a in sys.argv[1:] if not a.startswith("--server.port") and a != "--port"]
        sys.argv = ["streamlit", "run", app_path, "--server.port", str(port)] + filtered_args
    else:
        sys.argv = ["streamlit", "run", app_path] + sys.argv[1:]

    sys.exit(main())

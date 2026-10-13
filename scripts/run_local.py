"""
One-click Local Development Runner for Offline Farmer Voice Assistant.
Starts backend FastAPI on port 8000 and prints connection instructions.
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
    print("Starting Offline Farmer Voice Assistant Backend on http://localhost:8000...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ], cwd=backend_dir)

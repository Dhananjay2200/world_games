"""
WorldGames - Unified Full-Stack Launcher.
Starts both the FastAPI backend (port 8001) and Vite React frontend (port 5174)
in a single command (`python start.py`), with clean Ctrl+C shutdown on Windows & Unix.
"""

import os
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from app.config import get_settings

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def _find_npm() -> str:
    """Finds the npm executable across Windows and POSIX."""
    if platform.system() == "Windows":
        return shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
    return shutil.which("npm") or "npm"


def _stream_output(proc: subprocess.Popen, prefix: str) -> None:
    """Streams subprocess stdout/stderr lines prefixed with service name."""
    if not proc.stdout:
        return
    try:
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            print(f"[{prefix}] {line.rstrip()}", flush=True)
    except Exception:
        pass


def _terminate_tree(proc: subprocess.Popen, name: str) -> None:
    """Gracefully stops a subprocess and any child processes it spawned."""
    if proc is None or proc.poll() is not None:
        return
    print(f"[*] Stopping {name} (PID {proc.pid})...")
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.terminate()
            proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> int:
    settings = get_settings()
    npm_exe = _find_npm()

    if not FRONTEND_DIR.exists():
        print(f"[-] Frontend directory not found at: {FRONTEND_DIR}")
        return 1

    # Install frontend dependencies automatically if node_modules is missing
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[*] frontend/node_modules missing — running npm install...")
        install_res = subprocess.run([npm_exe, "install"], cwd=str(FRONTEND_DIR), check=False)
        if install_res.returncode != 0:
            print("[-] npm install failed. Please check Node.js/npm setup.")
            return install_res.returncode

    print("=" * 68)
    print(f" Starting {settings.APP_NAME} (Backend + Frontend)")
    print(f"   Backend API : http://{settings.HOST}:{settings.PORT}")
    print(f"   API Docs    : http://{settings.HOST}:{settings.PORT}/docs")
    print("   Frontend UI : http://127.0.0.1:5174/")
    print("   Admin Desk  : http://127.0.0.1:5174/admin")
    print(" Press Ctrl+C to stop both servers.")
    print("=" * 68)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    backend_cmd = [sys.executable, str(ROOT_DIR / "run_server.py")]
    frontend_cmd = [npm_exe, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5174"]

    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(ROOT_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(FRONTEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    t_back = threading.Thread(target=_stream_output, args=(backend_proc, "BACKEND"), daemon=True)
    t_front = threading.Thread(target=_stream_output, args=(frontend_proc, "FRONTEND"), daemon=True)
    t_back.start()
    t_front.start()

    stop_requested = False

    def _handle_sig(signum, frame):
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, _handle_sig)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_sig)

    try:
        while not stop_requested:
            back_rc = backend_proc.poll()
            front_rc = frontend_proc.poll()
            if back_rc is not None:
                print(f"[!] Backend exited unexpectedly with code {back_rc}. Shutting down...")
                return back_rc
            if front_rc is not None:
                print(f"[!] Frontend exited unexpectedly with code {front_rc}. Shutting down...")
                return front_rc
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[*] Shutting down WorldGames servers...")
        _terminate_tree(frontend_proc, "Frontend")
        _terminate_tree(backend_proc, "Backend")
        print("[+] All servers stopped cleanly.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Start the bot from the encrypted application bundle.

bundle.bin is a zip of the application, encrypted with Fernet; the key comes from the BUNDLE_KEY secret (or a local
bundle.key file). The archive is unpacked into a private temporary directory and bot.py is run from there with
the given arguments, e.g. `python run.py poll` or `python run.py refresh`.
"""
from __future__ import annotations

import io
import os
import runpy
import subprocess
import sys
import tempfile
import traceback
import warnings
import zipfile
from pathlib import Path

import requests
from cryptography.fernet import Fernet

HERE = Path(__file__).resolve().parent


def notify_admin(text: str):
    """Errors go to the admin privately, never into the (public) job log."""
    token, admin = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("ADMIN_ID")
    if token and admin:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          data={"chat_id": admin, "text": text[:4000]}, timeout=20)
        except requests.RequestException:
            pass


def main():
    warnings.filterwarnings("ignore")
    key = os.environ.get("BUNDLE_KEY") or (HERE / "bundle.key").read_text().strip()
    app = Path(tempfile.mkdtemp(prefix="app-"))
    raw = Fernet(key.encode()).decrypt((HERE / "bundle.bin").read_bytes())
    zipfile.ZipFile(io.BytesIO(raw)).extractall(app)
    extra = app / "requirements-app.txt"
    if extra.exists():
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r",
                            str(extra)], capture_output=True, text=True)
        if r.returncode:
            print("dependency install failed", flush=True)
            notify_admin("dependency install failed:\n" + r.stderr[-3000:])
            sys.exit(1)
    os.environ.setdefault("WX_WORK", str(HERE / "cache"))
    sys.argv = [str(app / "bot.py"), *sys.argv[1:]]
    try:
        runpy.run_path(str(app / "bot.py"), run_name="__main__")
    except SystemExit:
        raise
    except BaseException as e:
        print(f"run failed: {type(e).__name__}", flush=True)
        notify_admin("run failed:\n" + traceback.format_exc()[-3500:])
        sys.exit(1)


if __name__ == "__main__":
    main()

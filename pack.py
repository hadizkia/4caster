"""Build bundle.bin from the application files (zip, then Fernet-encrypt with the key in bundle.key).

    python pack.py            build bundle.bin (creates bundle.key on first use)
Put the key into the BUNDLE_KEY repository secret:  gh secret set BUNDLE_KEY < bundle.key
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parent
FILES = ["bot.py", "forecast.py", "llm.py", "wxkit.py", "sandbox.py", "agro.py", "farmx.py", "outlook.py", "requirements-app.txt"]
DIRS = ["fonts"]


def main():
    keyfile = ROOT / "bundle.key"
    if not keyfile.exists():
        keyfile.write_text(Fernet.generate_key().decode())
        print("new key written to bundle.key")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(ROOT / f, f)
        for d in DIRS:
            for p in sorted((ROOT / d).rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(ROOT).as_posix())
    blob = Fernet(keyfile.read_text().strip().encode()).encrypt(buf.getvalue())
    (ROOT / "bundle.bin").write_bytes(blob)
    print(f"bundle.bin: {len(blob) / 1024:.0f} KB, sha256 {hashlib.sha256(blob).hexdigest()[:12]}")


if __name__ == "__main__":
    main()

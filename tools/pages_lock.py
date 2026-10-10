#!/usr/bin/env python3
"""Password-gate the site's HTML pages with StatiCrypt (one password per section).

  python3 tools/pages_lock.py lock     # keep plaintext copies in .plain/ (gitignored), encrypt pages in place
  python3 tools/pages_lock.py unlock   # restore plaintext from .plain/ before running build scripts
  python3 tools/pages_lock.py check    # exit 1 if any tracked/staged page is plaintext (used by the pre-commit hook)

Passwords live in .pagelock.json (gitignored, chmod 600): {"root": "...", "ira": "...", "aukus": "...", "ndaa_korea": "..."}
Limits: StatiCrypt encrypts HTML only. CSV/JSON/PDF files and earlier commits in this public repository stay readable.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAIN = ROOT / ".plain"
CONF = ROOT / ".pagelock.json"
MARK = "staticrypt"  # string present in every encrypted page
SECTIONS = {"ira": "ira", "aukus": "aukus", "ndaa_korea": "ndaa_korea"}
TEMPLATE = ["--template-title", "비공개 자료", "--template-instructions", "이 자료는 비밀번호가 있어야 볼 수 있습니다.",
            "--template-button", "열기", "--template-placeholder", "비밀번호", "--template-error", "비밀번호가 맞지 않습니다.",
            "--template-remember", "이 기기에서 30일간 기억", "--template-color-primary", "#2f5fa8"]


def pages():
    """(section key, path) for every HTML page the site serves."""
    out = [("root", ROOT / "index.html")]
    for key, d in SECTIONS.items():
        for p in sorted((ROOT / d).rglob("*.html")):
            if "vendor" not in p.parts:
                out.append((key, p))
    return out


def is_locked(p):
    return MARK in p.read_text(encoding="utf-8", errors="ignore")[:20000]


def lock():
    pw = json.loads(CONF.read_text(encoding="utf-8"))
    todo = {}
    for key, p in pages():
        if is_locked(p):
            continue
        dst = PLAIN / p.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        todo.setdefault((key, p.parent), []).append(p)
    for (key, parent), files in todo.items():
        env = dict(os.environ, STATICRYPT_PASSWORD=pw["root"] if key == "coupang" and key not in pw else pw[key])
        cmd = ["npx", "--yes", "staticrypt@3", *[str(f) for f in files], "--short", "--remember", "30",
               "-d", str(parent), "--config", ".staticrypt.json", *TEMPLATE]
        subprocess.run(cmd, check=True, env=env, cwd=ROOT, stdout=subprocess.DEVNULL)
        print(f"locked {len(files):3d} page(s) in {parent.relative_to(ROOT) or '.'} [{key}]")
    for key, p in pages():
        namespace(p, key)
    bad = [p for _, p in pages() if not is_locked(p)]
    if bad:
        sys.exit(f"still plaintext: {bad}")


def namespace(p, key):
    """Give each section its own 'remember me' storage key (all sections share one origin)."""
    s = p.read_text(encoding="utf-8")
    t = s.replace('"staticrypt_passphrase"', f'"staticrypt_passphrase_{key}"').replace('"staticrypt_expiration"', f'"staticrypt_expiration_{key}"')
    if t != s:
        p.write_text(t, encoding="utf-8")


def unlock():
    n = 0
    for _, p in pages():
        src = PLAIN / p.relative_to(ROOT)
        if is_locked(p) and src.exists():
            shutil.copy2(src, p)
            n += 1
    print(f"restored {n} plaintext page(s) from .plain/")


def check():
    staged = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], cwd=ROOT,
                            capture_output=True, text=True).stdout.split()
    bad = []
    for f in staged:
        if f.endswith(".html") and "vendor/" not in f:
            blob = subprocess.run(["git", "show", f":{f}"], cwd=ROOT, capture_output=True, text=True).stdout
            if MARK not in blob[:20000]:
                bad.append(f)
    if bad:
        print("평문 HTML은 커밋할 수 없습니다. 먼저 `python3 tools/pages_lock.py lock`을 실행하세요:\n  " + "\n  ".join(bad))
        sys.exit(1)


if __name__ == "__main__":
    {"lock": lock, "unlock": unlock, "check": check}[sys.argv[1] if len(sys.argv) > 1 else "check"]()

#!/usr/bin/env python3
"""Encrypt a static HTML report into reports/<slug>/ behind a per-report password.

Usage: build_report_vault.py REPORT_DIR SLUG      (SLUG "new" makes a fresh pc-xxxxxx-style slug from --prefix)
       build_report_vault.py REPORT_DIR new --prefix pc

Every top-level *.html in REPORT_DIR is a page (index.html is the home page); every relative image/video/pdf a page quotes
(src/href/poster/data-*/JS strings) is encrypted as media. Scheme matches /diy: key = PBKDF2-HMAC-SHA256(password,
16-byte salt, 600k, 32 bytes); entry = IV(12) || AES-256-GCM(gzip(plaintext)). Entries get opaque names (m_000.enc);
the page/asset map is itself an encrypted entry, so manifest.json only holds KDF params and that entry's name.
Passwords live in ~/Documents/reports/.vault_passwords.json (mode 600), never in the site repo; an existing slug
reuses its password, so republishing keeps the same password.
"""
import argparse, base64, datetime, gzip, hashlib, json, mimetypes, os, re, secrets, shutil, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(SITE, "tools", "report_gate.html")
PW_FILE = os.path.expanduser("~/Documents/reports/.vault_passwords.json")
ITERS = 600_000
MEDIA_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp4", ".webm", ".pdf")
QUOTED = re.compile(r"""(['"])([^'"<>\s]+)\1""")


def words():
    ws = {w.strip() for w in open("/usr/share/dict/words") if re.fullmatch(r"[a-z]{4,7}", w.strip())}
    cracklib = set(open("/usr/share/dict/cracklib-small").read().split())
    common = sorted(ws & cracklib)
    return common if len(common) > 2000 else sorted(ws)


def new_password():
    ws = words()
    return "-".join(secrets.choice(ws) for _ in range(4)) + "-" + str(secrets.randbelow(90) + 10)


def load_passwords():
    if not os.path.exists(PW_FILE):
        return {}
    return json.load(open(PW_FILE))


def save_passwords(pw):
    fd = os.open(PW_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(pw, f, indent=1)
    os.chmod(PW_FILE, 0o600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_dir")
    ap.add_argument("slug")
    ap.add_argument("--prefix", default="r")
    a = ap.parse_args()
    src = os.path.abspath(a.report_dir)
    pw = load_passwords()
    slug = f"{a.prefix}-{secrets.token_hex(3)}" if a.slug == "new" else a.slug
    if slug not in pw:
        pw[slug] = {"password": new_password(), "report_dir": src}
        save_passwords(pw)
    password = pw[slug]["password"]

    pages = sorted(f[:-5] for f in os.listdir(src) if f.endswith(".html"))
    if "index" not in pages:
        sys.exit(f"{src} has no index.html")
    assets, missing = set(), set()
    for p in pages:
        for _, ref in QUOTED.findall(open(os.path.join(src, p + ".html")).read()):
            if re.match(r"^[a-z]+:|^#|^/", ref) or not ref.lower().endswith(MEDIA_EXT):
                continue
            path = os.path.normpath(os.path.join(src, ref))
            if not path.startswith(src + os.sep):
                continue
            (assets if os.path.isfile(path) else missing).add(ref)
    if missing:
        sys.exit(f"pages reference {len(missing)} missing files, e.g. {sorted(missing)[:5]}")

    out = os.path.join(SITE, "reports", slug)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    salt = os.urandom(16)
    aes = AESGCM(hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERS, 32))
    n = [0]
    total = [0]

    def enc(data):
        name = f"m_{n[0]:03d}.enc"
        n[0] += 1
        iv = os.urandom(12)
        blob = iv + aes.encrypt(iv, gzip.compress(data, 6), None)
        open(os.path.join(out, name), "wb").write(blob)
        total[0] += len(blob)
        return name

    order = list(pages) + sorted(assets)
    secrets.SystemRandom().shuffle(order)   # entry numbers carry no hint of page vs asset
    index = {"home": "index", "pages": {}, "media": {}}
    for item in order:
        if item in pages:
            index["pages"][item] = enc(open(os.path.join(src, item + ".html"), "rb").read())
        else:
            mime = mimetypes.guess_type(item)[0] or "application/octet-stream"
            index["media"][item] = {"file": enc(open(os.path.join(src, item), "rb").read()), "mime": mime}
    built = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    manifest = {"version": 3, "compression": "gzip", "built": built, "cipher": "AES-GCM",
                "kdf": {"name": "PBKDF2", "hash": "SHA-256", "iterations": ITERS, "salt": base64.b64encode(salt).decode()},
                "index": enc(json.dumps(index).encode())}
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    shutil.copy(GATE, os.path.join(out, "index.html"))
    print(f"{slug}: {len(pages)} pages, {len(assets)} assets, {total[0] / 1e6:.1f} MB -> reports/{slug}/")


if __name__ == "__main__":
    main()

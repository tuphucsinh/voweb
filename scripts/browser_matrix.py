#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html.parser
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VIEWPORTS = ((390, 844), (430, 900), (768, 1024), (1024, 900), (1440, 900), (1920, 1080))
ROUTES = (
    ("vi-home", "/vi/", "vi"),
    ("en-home", "/en/", "en"),
    ("vi-about", "/vi/gioi-thieu/", "vi"),
    ("en-about", "/en/about/", "en"),
    ("vi-brands", "/vi/thuong-hieu/", "vi"),
    ("en-brands", "/en/brands/", "en"),
    ("vi-marigold", "/vi/thuong-hieu/marigold/", "vi"),
    ("en-marigold", "/en/brands/marigold/", "en"),
    ("vi-product", "/vi/san-pham/marigold-orange/", "vi"),
    ("en-product", "/en/products/marigold-orange/", "en"),
    ("vi-capabilities", "/vi/nang-luc/", "vi"),
    ("en-capabilities", "/en/capabilities/", "en"),
    ("vi-partners", "/vi/doi-tac/", "vi"),
    ("en-partners", "/en/partners/", "en"),
    ("vi-insights", "/vi/goc-nhin/", "vi"),
    ("en-insights", "/en/insights/", "en"),
    ("vi-contact", "/vi/lien-he/", "vi"),
    ("en-contact", "/en/contact/", "en"),
)

class ImageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.images: list[dict[str, str | None]] = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))

def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "VOweb-browser-matrix/1"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, response.read().decode("utf-8", "replace")

def local_image_checks(base: str, document: str) -> list[str]:
    parser = ImageParser(); parser.feed(document)
    errors = []
    for attrs in parser.images:
        src = attrs.get("src") or ""
        if not src or src.startswith(("http:", "https:", "data:", "//")):
            continue
        decorative_icon = src.startswith("/assets/ui-icons/")
        if not decorative_icon and not (attrs.get("alt") or "").strip():
            errors.append(f"missing alt: {src}")
        try:
            if int(attrs.get("width") or "0") <= 0 or int(attrs.get("height") or "0") <= 0:
                errors.append(f"invalid geometry: {src}")
        except ValueError:
            errors.append(f"non-numeric geometry: {src}")
        asset_url = urllib.parse.urljoin(base, src)
        try:
            status, _ = fetch(asset_url)
            if status != 200:
                errors.append(f"asset HTTP {status}: {src}")
        except Exception as exc:
            errors.append(f"asset unavailable: {src} ({type(exc).__name__})")
    return errors

def source_contract_checks(route: str, document: str) -> list[str]:
    errors = []
    if not re.search(r'<html\b[^>]*\blang="(?:vi|en)"', document):
        errors.append("missing html lang")
    if route.endswith("/doi-tac/") or route.endswith("/partners/"):
        if "partners-hero" not in document or "b2b-vorigin-premium.webp" in document:
            errors.append("Partners hero contract failed")
    if route.endswith("/lien-he/") or route.endswith("/contact/"):
        form = document.find('class="form-wrap')
        aside = document.find('class="contact-aside')
        if form < 0 or aside < 0 or form > aside:
            errors.append("Contact form must precede aside in DOM")
    if 'class="menu-toggle"' not in document or 'aria-controls="primary-nav"' not in document:
        errors.append("mobile menu control missing")
    return errors

def run_matrix(base: str, evidence: Path) -> int:
    evidence.mkdir(parents=True, exist_ok=True)
    source_failures = 0
    for name, route, locale in ROUTES:
        url = base.rstrip("/") + route
        try:
            status, document = fetch(url)
        except Exception as exc:
            print(f"FAIL {name}: server unavailable ({type(exc).__name__})")
            return 2
        if status != 200:
            print(f"FAIL {name}: HTTP {status}")
            return 2
        source_errors = source_contract_checks(route, document) + local_image_checks(base, document)
        if source_errors:
            source_failures += 1
            print(f"FAIL {name} source contract — {', '.join(source_errors)}")
        else:
            print(f"PASS {name} source contract")

    probe = subprocess.run(
        ["node", str(Path(__file__).with_name("browser_matrix_cdp.mjs")), "--base-url", base, "--evidence-dir", str(evidence)],
        capture_output=True,
        text=True,
        timeout=900,
    )
    if probe.stdout:
        print(probe.stdout, end="")
    if probe.stderr:
        print(probe.stderr, end="", file=sys.stderr)
    return 1 if source_failures or probe.returncode else 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--evidence-dir", default="/home/pi5/hermes-artifacts/browser-evidence/VOweb/browser-matrix")
    args = parser.parse_args()
    return run_matrix(args.base_url, Path(args.evidence_dir))

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Rendert assets/og.jpg (1200x630) aus dem Hero der lokal servierten Seite.

    python3 -m http.server 8000 &   # im Repo-Root
    python3 scripts/make_og.py
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("PORTFOLIO_BASE", "http://127.0.0.1:8000/")
OUT = Path(__file__).resolve().parent.parent / "assets" / "og.jpg"

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1200, "height": 630})
    page.goto(BASE, wait_until="networkidle")
    page.add_style_tag(content=".topbar .lang, .chapters, .rail, #ueber { visibility: hidden; }")
    page.wait_for_timeout(2500)  # Schwarm hat sich formiert, Sonar-Ringe stehen
    page.screenshot(path=str(OUT), type="jpeg", quality=82)
    browser.close()
print(OUT, OUT.stat().st_size)

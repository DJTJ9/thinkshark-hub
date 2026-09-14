#!/usr/bin/env python3
"""Visuelle + funktionale Verifikation der Portfolioseite (Playwright, kein MCP).

BASE/HUB sind per Umgebungsvariable überschreibbar, damit dieses Script auch
gegen einen lokalen Server laufen kann, bevor der Livegang (Task 7) passiert
ist:

    PORTFOLIO_BASE=http://127.0.0.1:8000/ PORTFOLIO_HUB=http://127.0.0.1:8000/hub.html \
        python3 scripts/verify_portfolio.py

Ohne Umgebungsvariablen wird gegen die Live-URLs geprüft.
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("/tmp/portfolio-verify")
BASE = os.environ.get("PORTFOLIO_BASE", "https://thinkshark.de")
HUB = os.environ.get("PORTFOLIO_HUB", "https://hub.thinkshark.de")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fails = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        for label, size in [("desktop", (1280, 800)), ("mobile", (390, 844))]:
            page = browser.new_page(viewport={"width": size[0], "height": size[1]})
            errors = []
            page.on("console", lambda m: m.type == "error" and errors.append(m.text))
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(BASE, wait_until="networkidle")
            page.screenshot(path=str(OUT / f"portfolio-{label}.png"), full_page=True)

            hscroll = page.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            if hscroll:
                fails.append(f"{label}: horizontales Scrollen")
            if errors:
                fails.append(f"{label}: Konsolen-Fehler beim Laden {errors}")
            errors_at_load = len(errors)

            mail = page.evaluate("document.getElementById('mail').getAttribute('href')")
            if not mail.startswith("mailto:TjarkDreyer@"):
                fails.append(f"{label}: Mail nicht deobfuskiert ({mail})")

            shots = page.evaluate(
                """
                Array.from(document.querySelectorAll('.project__shot img')).map((img, i) => {
                  const r = img.getBoundingClientRect();
                  return {i, w: r.width, h: r.height};
                })
                """
            )
            for shot in shots:
                w, h = shot["w"], shot["h"]
                if h <= 0 or abs(w / h - 16 / 10) > 0.05:
                    fails.append(
                        f"{label}: .project__shot img[{shot['i']}] falsches Seitenverhältnis "
                        f"({w:.0f}x{h:.0f})"
                    )

            page.click(".lang__btn[data-lang='en']")
            if "Who I am" not in page.content():
                fails.append(f"{label}: EN-Umschaltung greift nicht")
            page.reload(wait_until="networkidle")
            if page.evaluate("document.documentElement.lang") != "en":
                fails.append(f"{label}: Sprachwahl überlebt Reload nicht")
            page.click(".lang__btn[data-lang='de']")
            new_errors = errors[errors_at_load:]
            if new_errors:
                fails.append(f"{label}: Konsolen-Fehler nach Interaktion {new_errors}")
            page.close()

        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(HUB, wait_until="networkidle")
        page.screenshot(path=str(OUT / "hub-desktop.png"), full_page=True)
        if page.locator(".hub-card").count() != 4:
            fails.append("hub: nicht 4 Tool-Karten")
        page.close()
        browser.close()

    for f in fails:
        print("FAIL:", f)
    print(f"Screenshots: {OUT}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

SUBS = ["app", "code", "job-scanner", "organizer"]

def test_all_four_subdomain_links_present():
    for sub in SUBS:
        assert f'https://{sub}.thinkshark.de' in HTML, f"missing link for {sub}"

def test_sync_subdomain_absent():
    assert "sync.thinkshark.de" not in HTML

def test_external_links_are_safe():
    anchors = re.findall(r'<a\b[^>]*https://[a-z-]+\.thinkshark\.de[^>]*>', HTML)
    assert len(anchors) == 4
    for a in anchors:
        assert 'target="_blank"' in a
        assert 'rel="noopener"' in a

def test_reduced_motion_guard_in_css():
    assert "prefers-reduced-motion" in CSS

def test_accent_palette_present():
    assert "#3DE1C0" in CSS
    assert "#0A1420" in CSS

def test_mono_font_for_urls():
    assert "hub-card__url" in HTML
    assert "IBM Plex Mono" in CSS

def test_no_framework_build_artifacts():
    assert not (ROOT / "package.json").exists()

def test_fonts_are_self_hosted():
    assert "fonts.googleapis" not in HTML
    assert "fonts.gstatic" not in HTML
    assert 'href="fonts.css"' in HTML
    fonts_css = (ROOT / "fonts.css").read_text(encoding="utf-8")
    assert "https://" not in fonts_css  # all @font-face src are local
    assert "font-display: swap" in fonts_css

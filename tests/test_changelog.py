import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "changelog.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "changelog.js").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def test_changelog_links_shared_assets():
    assert 'href="fonts.css"' in HTML
    assert 'href="styles.css"' in HTML
    assert 'src="changelog.js"' in HTML


def test_flare_token_defined_and_member_scoped():
    assert "--flare: #FFB454" in CSS
    assert CSS.count("var(--flare)") == 2  # nur border + Titel des Member-Blocks


def test_ping_animation_respects_reduced_motion():
    assert "@keyframes ping" in CSS
    tail = CSS[CSS.rfind("prefers-reduced-motion"):]
    assert ".entry--latest .entry__echo::after { animation: none; }" in tail


def test_patches_json_valid_and_shaped():
    data = json.loads((ROOT / "patches.json").read_text(encoding="utf-8"))
    assert "generated" in data
    assert isinstance(data["patches"], list)


def test_index_links_changelog():
    assert 'href="changelog.html"' in INDEX


def test_js_escapes_content_and_fetches_relative():
    assert "textContent" in JS  # esc() nutzt DOM-Escaping
    assert 'fetch("patches.json")' in JS


def test_empty_state_present():
    assert "Noch keine Patches" in HTML


def test_back_link_to_index():
    assert 'href="index.html"' in HTML

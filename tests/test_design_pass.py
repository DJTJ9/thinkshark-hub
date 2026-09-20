import re
from pathlib import Path

from html_utils import parse_elements, rules_for_selector

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "main.js").read_text(encoding="utf-8")
DEPTH_COLOURS = ["#14506B", "#0E2F47", "#0A1A2B", "#050B14"]


def _lum(hex_colour):
    h = hex_colour.lstrip("#")
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    chans = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def _contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _var(name):
    """Wert einer Farbvariable, wie sie auf .portfolio gilt (Override vor :root)."""
    for selector in (".portfolio", ":root"):
        for rule in rules_for_selector(CSS, selector):
            m = re.search(re.escape(name) + r":\s*(#[0-9A-Fa-f]{6})", rule["body"])
            if m:
                return m.group(1)
    raise AssertionError(f"{name} nicht definiert")


def test_background_follows_the_depth_variable():
    rules = rules_for_selector(CSS, "body.portfolio::before")
    assert rules, "kein Tiefenverlauf auf body.portfolio::before"
    body = rules[0]["body"]
    positions = [body.index(c) for c in DEPTH_COLOURS]
    assert positions == sorted(positions), "Tiefenfarben fehlen oder stehen in falscher Reihenfolge"
    assert "background-size: 100% 400%" in body
    assert "var(--depth" in body, "Verlauf hängt nicht an --depth"
    assert "animation: none" in body, "drift läuft weiter — Motion-Inventar ist abgeschlossen"


def test_main_js_publishes_the_scroll_depth():
    assert '"--depth"' in JS and "scrollHeight" in JS and "requestAnimationFrame" in JS
    assert "passive: true" in JS


def test_light_rays_fade_out_by_40_metres():
    rules = rules_for_selector(CSS, "body.portfolio::after")
    assert rules, "keine Lichtstrahlen"
    assert "opacity: calc(1 - var(--depth, 0) * 5)" in rules[0]["body"]
    assert "pointer-events: none" in rules[0]["body"]


def test_text_colours_stay_aa_on_every_depth_colour():
    for name in ("--foam", "--mist", "--teal"):
        for bg in DEPTH_COLOURS:
            ratio = _contrast(_var(name), bg)
            assert ratio >= 4.5, f"{name} auf {bg}: nur {ratio:.2f}:1"

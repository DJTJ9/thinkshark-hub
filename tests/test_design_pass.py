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


SEA = (ROOT / "sea.js").read_text(encoding="utf-8") if (ROOT / "sea.js").exists() else ""
SEA_PAGES = ["index.html", "projekt-izzy.html", "projekt-bullseyeq.html",
             "projekt-bob.html", "projekt-desk-buddy.html"]
NO_SEA_PAGES = ["hub.html", "impressum.html", "datenschutz.html", "changelog.html"]


def _scripts(name):
    html = (ROOT / name).read_text(encoding="utf-8")
    return [a for t, a in parse_elements(html) if t == "script"]


def test_sea_runs_on_portfolio_pages_only():
    for name in SEA_PAGES:
        sea = [a for a in _scripts(name) if a.get("src") == "sea.js"]
        assert len(sea) == 1 and "defer" in sea[0], f"{name}: sea.js fehlt oder blockiert das Parsen"
    for name in NO_SEA_PAGES:
        assert not any(a.get("src") == "sea.js" for a in _scripts(name)), f"{name}: sea.js gehört hier nicht hin"


def test_sea_canvas_never_blocks_the_page():
    rules = rules_for_selector(CSS, ".portfolio .sea")
    assert rules, "keine Regel für das Canvas"
    body = rules[0]["body"]
    for needle in ("position: fixed", "pointer-events: none", "z-index: -1"):
        assert needle in body, f"Canvas ohne „{needle}\""
    assert 'setAttribute("aria-hidden", "true")' in SEA


def test_sea_guard_rails():
    assert SEA.lstrip().startswith("//") and "(function () {" in SEA, "sea.js ist keine IIFE"
    assert "Math.min(window.devicePixelRatio || 1, 1.5)" in SEA, "DPR nicht auf 1.5 gedeckelt"
    assert "visibilitychange" in SEA and "document.hidden" in SEA, "Loop pausiert nicht im Hintergrund-Tab"
    assert "prefers-reduced-motion" in SEA, "reduced motion wird nicht beachtet"
    assert "const FISH_ALPHA = 0.35;" in SEA, "Fisch-Deckkraft nicht auf 35 % gedeckelt"
    assert "STILL_FISH = 8" in SEA
    assert 'classList.contains("detail")' in SEA, "Detailseiten bekämen den Schwarm"
    assert "window.innerWidth < 900 ? 14 : 36" in SEA


def test_readme_deploys_the_sea():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "sea.js" in readme[readme.index("Redeploy"):readme.index("Caddy-Reload")], \
        "sea.js fehlt im Redeploy-cp"


INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def test_project_shots_are_framed_as_finds():
    tags = [a for t, a in parse_elements(INDEX) if t == "figcaption" and "project__depth" in (a.get("class") or "")]
    assert len(tags) == 4, "nicht jedes Projektbild trägt seine Tiefe"
    texts = re.findall(r'<figcaption class="project__depth">([^<]+)<', INDEX)
    assert texts == ["60 m", "90 m", "120 m", "150 m"]
    frame = rules_for_selector(CSS, ".portfolio .project__shot::before")
    assert frame and frame[0]["body"].count("linear-gradient") == 8, "keine vier Sonar-Eckklammern"


def test_one_sonar_ping_per_project_image():
    assert "@keyframes found-ping" in CSS
    ring = rules_for_selector(CSS, ".portfolio .project__shot.is-found::after")
    assert ring and "animation: found-ping" in ring[0]["body"] and " 1 " in ring[0]["body"] + " ", \
        "Ping läuft nicht genau einmal"
    reduced = rules_for_selector(CSS, ".portfolio .project__shot.is-found::after", media="prefers-reduced-motion")
    assert reduced and "animation: none" in reduced[0]["body"]
    assert "is-found" in JS and "unobserve" in JS, "Ping würde bei jedem Reinscrollen neu feuern"


def test_contact_carries_the_amber_lure():
    lure = rules_for_selector(CSS, ".portfolio #kontakt h2::before")
    assert lure and "var(--flare)" in lure[0]["body"] and "animation" not in lure[0]["body"]


def test_rail_depths_use_tabular_figures():
    rules = rules_for_selector(CSS, ".portfolio .rail__depth")
    assert any("font-variant-numeric: tabular-nums" in r["body"] for r in rules)


def test_portrait_sits_inside_the_sonar_rings():
    photo = rules_for_selector(CSS, ".portfolio .hero__photo img")
    assert any("border-radius: 50%" in r["body"] for r in photo), "Porträt ist nicht rund"
    assert rules_for_selector(CSS, ".portfolio .hero__ping", media="min-width: 1000px"), \
        "Ringe sind auf dem Desktop nicht auf das Porträt zentriert"

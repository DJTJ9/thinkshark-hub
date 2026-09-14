import re
from pathlib import Path

from html_utils import parse_elements, rules_for_selector

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "main.js").read_text(encoding="utf-8")


def test_hero_says_games_programmer():
    assert "Tjark Dreyer" in HTML
    assert "Games Programmer" in HTML
    assert "Full-Stack Developer" not in HTML


def test_tool_subdomains_no_longer_on_apex():
    for sub in ["app", "code", "job-scanner", "organizer"]:
        assert f"https://{sub}.thinkshark.de" not in HTML
    assert 'href="hub.html"' in HTML


def test_all_sections_present_with_depth():
    for sid in ["ueber", "projekte", "lebenslauf", "kontakt"]:
        assert f'id="{sid}"' in HTML
    depths = re.findall(r'data-depth="(\d+)"', HTML)
    assert depths == ["0", "20", "60", "90", "120", "150", "180"]


def test_rail_is_present_and_static():
    elements = parse_elements(HTML)
    assert any(tag == "aside" and "rail" in (attrs.get("class") or "").split() for tag, attrs in elements), \
        "kein <aside class=\"rail\"> im Markup"
    assert any(tag == "span" and "rail__marker" in (attrs.get("class") or "").split() for tag, attrs in elements), \
        "kein .rail__marker-Element im Markup"
    rules = rules_for_selector(CSS, ".rail__marker")
    assert any("position: sticky" in r["body"] for r in rules), \
        ".rail__marker hat keine position: sticky-Regel"


def test_four_projects_in_strength_order():
    order = [m.strip() for m in re.findall(r'class="project__title"[^>]*>([^<]+)<', HTML)]
    assert order == ["Izzy's Island Party", "BullseyeQ", "Bob der Job-Bot", "Desk-Buddy"]


def test_repo_links_present_except_desk_buddy():
    assert "https://github.com/DJTJ9/IzzysIslandParty" in HTML
    assert "https://github.com/DJTJ9/BullseyeQ" in HTML
    assert "https://github.com/DJTJ9/job-scanner" in HTML
    desk = HTML[HTML.index("Desk-Buddy"):]
    assert "github.com/DJTJ9/desk" not in desk.lower()


def test_desk_buddy_marked_in_progress():
    elements = parse_elements(HTML)
    assert any("badge--wip" in (attrs.get("class") or "").split() for _, attrs in elements), \
        "kein Element mit class badge--wip im Markup"
    rules = rules_for_selector(CSS, ".badge--wip")
    assert rules, "keine CSS-Regel für .badge--wip"
    body = rules[0]["body"]
    assert "color: var(--flare)" in body
    assert "border" in body and "var(--flare)" in body


def test_project_images_have_fixed_ratio():
    imgs = [attrs for tag, attrs in parse_elements(HTML) if tag == "img"]
    project_imgs = [a for a in imgs if (a.get("src") or "").startswith("assets/projects/")]
    assert len(project_imgs) == 4
    for attrs in project_imgs:
        alt = attrs.get("alt")
        assert alt, f"leeres oder fehlendes alt bei {attrs.get('src')}"
        width, height = attrs.get("width"), attrs.get("height")
        assert width and height, f"fehlende width/height bei {attrs.get('src')}"
        assert int(width) * 10 == int(height) * 16, (
            f"{attrs.get('src')} hat kein 16:10-Attributverhältnis: {width}x{height}"
        )
    rules = rules_for_selector(CSS, ".project__shot img")
    assert rules, "keine CSS-Regel für .project__shot img"
    assert "aspect-ratio: 16 / 10" in rules[0]["body"]


def test_cv_downloads_linked():
    assert 'href="assets/cv/cv-de.pdf"' in HTML
    assert 'href="assets/cv/cv-en.pdf"' in HTML


def test_contact_links_without_phone():
    assert "https://github.com/DJTJ9" in HTML
    assert "linkedin.com/in/tjark-dreyer-179a30377" in HTML
    assert "0171" not in HTML
    assert not re.search(r"\+49", HTML)


def test_legal_pages_linked():
    assert 'href="impressum.html"' in HTML
    assert 'href="datenschutz.html"' in HTML


def test_no_generic_decorations():
    assert "Enter the waters" not in HTML
    assert "ansehen →" not in HTML


def test_focus_style_visible():
    for selector in ("a:focus-visible", "button:focus-visible"):
        rules = rules_for_selector(CSS, selector)
        assert rules, f"keine Regel für {selector}"
        assert any("outline: 2px solid var(--teal)" in r["body"] for r in rules), \
            f"{selector} hat keinen sichtbaren teal-Outline"


def test_every_translatable_node_has_both_languages():
    nodes = [attrs for _, attrs in parse_elements(HTML) if "data-de" in attrs or "data-en" in attrs]
    assert len(nodes) >= 12
    for attrs in nodes:
        de, en = attrs.get("data-de"), attrs.get("data-en")
        assert de and en, f"data-de/data-en fehlt oder leer auf einem Element: {attrs}"


def test_language_choice_persists_in_localstorage():
    assert 'localStorage' in JS
    assert '"lang"' in JS or "'lang'" in JS
    assert 'document.documentElement.lang' in JS


def test_mail_is_obfuscated_in_markup():
    assert "TjarkDreyer@gmail.com" not in HTML
    assert 'data-user="TjarkDreyer"' in HTML
    assert "mailto:" in JS


def test_sonar_ping_guarded_for_pages_without_cards():
    ping_block = JS[JS.index("Sonar-Ping"):]
    assert 'if (!reduce) {' in ping_block
    assert 'querySelectorAll(".hub-card")' in ping_block
    assert 'if (!ring) return;' in ping_block


def test_rail_marker_uses_intersection_observer():
    assert "IntersectionObserver" in JS
    assert "rail__marker" in JS


def test_hero_sweep_animates_once_and_respects_reduced_motion():
    assert "@keyframes sweep" in CSS
    assert ".portfolio .hero__sweep { transform-origin: left; animation: sweep 0.9s ease-out both; }" in CSS
    tail = CSS[CSS.rfind("prefers-reduced-motion"):]
    assert ".portfolio .hero__sweep { animation: none; opacity: 0; }" in tail

import re
from pathlib import Path

from html_utils import element_ids, fragment, has_class, parse_css_rules, parse_elements, rules_for_selector

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
    ids = element_ids(HTML)
    for sid in ["start", "ueber", "projekte", "izzy", "bullseyeq", "bob", "desk-buddy", "lebenslauf", "kontakt"]:
        assert sid in ids, f"Sprungziel #{sid} fehlt im Dokument"
    depths = re.findall(r'data-depth="(\d+)"', HTML)
    assert depths == ["0", "20", "60", "90", "120", "150", "180", "200"]


def test_lebenslauf_and_kontakt_are_separate_sections():
    sections = [attrs for tag, attrs in parse_elements(HTML) if tag == "section"]
    by_id = {a.get("id"): a for a in sections if a.get("id")}
    assert by_id["lebenslauf"].get("data-depth") == "180"
    assert by_id["kontakt"].get("data-depth") == "200"


def test_depth_scale_matches_max_depth():
    assert "const MAX_DEPTH = 200;" in JS
    rules = rules_for_selector(CSS, ".rail__scale li")
    assert rules, "keine Regel für .rail__scale li"
    assert "var(--at) / 200" in rules[0]["body"], \
        "CSS-Tiefenskala passt nicht zu MAX_DEPTH in main.js"


RAIL_TARGETS = ["#start", "#ueber", "#izzy", "#bullseyeq", "#bob", "#desk-buddy", "#lebenslauf", "#kontakt"]


def test_rail_is_a_labelled_navigation():
    elements = parse_elements(HTML)
    rails = [attrs for tag, attrs in elements if tag == "nav" and has_class(attrs, "rail")]
    assert rails, 'kein <nav class="rail"> im Markup'
    assert "aria-hidden" not in rails[0], "die Rail ist Navigation und darf nicht aria-hidden sein"
    assert rails[0].get("aria-label"), "die Rail-Navigation hat kein aria-label"
    assert not any(tag == "aside" and has_class(attrs, "rail") for tag, attrs in elements), \
        "die Rail ist noch ein <aside>"
    assert any(tag == "span" and has_class(attrs, "rail__marker") for tag, attrs in elements)
    assert any("position: sticky" in r["body"] for r in rules_for_selector(CSS, ".rail__marker"))


def test_every_rail_entry_links_to_an_existing_id():
    rail = fragment(HTML, '<ol class="rail__scale"', "</ol>")
    links = [attrs for tag, attrs in parse_elements(rail) if tag == "a"]
    assert [a.get("href") for a in links] == RAIL_TARGETS
    ids = element_ids(HTML)
    for a in links:
        assert a["href"][1:] in ids, f"Rail-Ziel {a['href']} existiert nicht im Dokument"


def test_every_rail_entry_carries_depth_and_label():
    rail = fragment(HTML, '<ol class="rail__scale"', "</ol>")
    elements = parse_elements(rail)
    assert len([a for t, a in elements if t == "span" and has_class(a, "rail__depth")]) == 8
    assert len([a for t, a in elements if t == "span" and has_class(a, "rail__label")]) == 8


def test_rail_column_is_wide_enough_for_labels():
    rules = rules_for_selector(CSS, ".layout")
    assert rules, "keine .layout-Regel"
    assert "grid-template-columns: 168px" in rules[0]["body"]


def test_rail_marks_the_active_entry():
    active = rules_for_selector(CSS, '.portfolio .rail__scale a[aria-current="true"] .rail__label')
    assert active, "kein aktiver Zustand für Rail-Labels"
    assert "color: var(--teal)" in active[0]["body"]
    assert "aria-current" in JS and "rail__scale" in JS


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

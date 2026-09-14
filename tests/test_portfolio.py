import re
from pathlib import Path

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
    assert 'class="rail"' in HTML
    assert "rail__marker" in HTML
    assert "position: sticky" in CSS


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
    assert "badge--wip" in HTML
    assert "var(--flare)" in CSS


def test_project_images_have_fixed_ratio():
    assert "assets/projects/izzy.png" in HTML
    assert "aspect-ratio" in CSS
    assert HTML.count("<img") == HTML.count("alt=")


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
    assert ":focus-visible" in CSS
    assert "outline: 2px solid var(--teal)" in CSS


def test_every_translatable_node_has_both_languages():
    de = re.findall(r'data-de="', HTML)
    en = re.findall(r'data-en="', HTML)
    assert len(de) == len(en) and len(de) >= 12


def test_language_choice_persists_in_localstorage():
    assert 'localStorage' in JS
    assert '"lang"' in JS or "'lang'" in JS
    assert 'document.documentElement.lang' in JS


def test_mail_is_obfuscated_in_markup():
    assert "TjarkDreyer@gmail.com" not in HTML
    assert 'data-user="TjarkDreyer"' in HTML
    assert "mailto:" in JS


def test_sonar_ping_guarded_for_pages_without_cards():
    assert ".hub-card" in JS
    assert "prefers-reduced-motion" in JS


def test_rail_marker_uses_intersection_observer():
    assert "IntersectionObserver" in JS
    assert "rail__marker" in JS

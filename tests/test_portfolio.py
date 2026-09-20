import re
from pathlib import Path

from html_utils import (element_ids, fragment, has_class, parse_css_rules, parse_elements,
                        rules_for_selector, text_by_class)

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
    base = rules_for_selector(CSS, ".portfolio .hero__sweep")
    assert any("animation: sweep 0.9s ease-out both" in r["body"] for r in base if r["media"] is None)
    reduced = rules_for_selector(CSS, ".portfolio .hero__sweep", media="prefers-reduced-motion")
    assert reduced, "kein reduced-motion-Override für .hero__sweep"
    assert "animation: none" in reduced[0]["body"]


def test_chapter_bar_mirrors_the_rail_targets():
    chapters = fragment(HTML, '<nav class="chapters"', "</nav>")
    links = [attrs for tag, attrs in parse_elements(chapters) if tag == "a"]
    assert [a.get("href") for a in links] == RAIL_TARGETS
    navs = [a for tag, a in parse_elements(HTML) if tag == "nav" and has_class(a, "chapters")]
    assert navs and navs[0].get("aria-label"), "Kapitelleiste ohne aria-label"


def test_exactly_one_navigation_is_visible_per_viewport():
    base = rules_for_selector(CSS, ".portfolio .chapters")
    assert any(r["media"] is None and "display: none" in r["body"] for r in base), \
        "Kapitelleiste ist auf dem Desktop nicht ausgeblendet"
    mobile = rules_for_selector(CSS, ".portfolio .chapters", media="max-width: 899px")
    assert any("display: flex" in r["body"] for r in mobile), \
        "Kapitelleiste erscheint unter 900px nicht"
    rail_hidden = rules_for_selector(CSS, ".rail__scale", media="max-width: 899px")
    assert any("display: none" in r["body"] for r in rail_hidden), \
        "Rail-Labels bleiben unter 900px sichtbar — zwei Navigationen gleichzeitig"


def test_chapter_bar_is_sticky_and_scrolls_the_active_entry_into_view():
    base = rules_for_selector(CSS, ".portfolio .chapters")
    body = next(r["body"] for r in base if r["media"] is None)
    assert "position: sticky" in body
    assert "overflow-x: auto" in body
    assert "scrollIntoView" in JS and "chapters" in JS


def test_hero_has_three_sonar_rings():
    ping = fragment(HTML, '<div class="hero__ping"', "</div>")
    spans = [a for tag, a in parse_elements(ping) if tag == "span"]
    assert len(spans) == 3, f"{len(spans)} Ringe statt 3"
    assert "@keyframes ping-in" in CSS
    base = rules_for_selector(CSS, ".portfolio .hero__ping span")
    assert base, "keine Regel für .portfolio .hero__ping span"
    assert "animation: ping-in" in base[0]["body"]
    delays = []
    for n in (1, 2, 3):
        rules = rules_for_selector(CSS, f".portfolio .hero__ping span:nth-child({n})")
        assert rules, f"keine Regel für Ring {n}"
        delays.append(rules[0]["body"])
    assert "animation-delay: 0s" in delays[0]
    assert "animation-delay: 0.35s" in delays[1]
    assert "animation-delay: 0.7s" in delays[2]


def test_sonar_rings_stop_at_a_faint_resting_state():
    tail = CSS[CSS.index("@keyframes ping-in"):]
    end = tail[:tail.index("}\n")]
    assert "opacity: 0.10" in tail[:tail.index("\n}")], \
        "Ringe verschwinden am Ende statt schwach stehenzubleiben"


def test_hero_ping_respects_reduced_motion():
    rules = rules_for_selector(CSS, ".portfolio .hero__ping span", media="prefers-reduced-motion")
    assert rules, "keine reduced-motion-Regel für die Sonar-Ringe"
    assert "animation: none" in rules[0]["body"]
    assert "opacity: 0.10" in rules[0]["body"], "Endzustand wird bei reduced motion nicht gesetzt"


def test_hero_photo_slot_is_square_and_shift_free():
    imgs = [a for tag, a in parse_elements(HTML) if tag == "img" and a.get("src") == "assets/me.jpg"]
    assert len(imgs) == 1, "kein (oder mehr als ein) Foto-Slot im Hero"
    attrs = imgs[0]
    assert attrs.get("alt"), "Foto-Slot ohne alt"
    assert attrs.get("width") and attrs.get("height"), "Foto-Slot ohne width/height (Layout-Shift)"
    assert attrs["width"] == attrs["height"], "Foto-Slot ist nicht 1:1"
    rules = rules_for_selector(CSS, ".portfolio .hero__photo img")
    assert rules, "keine Regel für .portfolio .hero__photo img"
    body = rules[0]["body"]
    assert "aspect-ratio: 1 / 1" in body
    # Learning 2026-09-14: ohne height:auto gewinnt das height-Attribut gegen aspect-ratio
    assert "height: auto" in body


DETAIL_BY_SECTION = {
    "izzy": "projekt-izzy.html",
    "bullseyeq": "projekt-bullseyeq.html",
    "bob": "projekt-bob.html",
    "desk-buddy": "projekt-desk-buddy.html",
}


def test_each_project_card_links_its_detail_page():
    for section_id, page in DETAIL_BY_SECTION.items():
        block = fragment(HTML, f'<section id="{section_id}"', "</section>")
        hrefs = {a.get("href") for tag, a in parse_elements(block) if tag == "a"}
        assert page in hrefs, f"Projektkarte #{section_id} verlinkt {page} nicht"


def test_more_link_is_bilingual_and_keeps_the_repo_link():
    for section_id, page in DETAIL_BY_SECTION.items():
        block = fragment(HTML, f'<section id="{section_id}"', "</section>")
        more = [a for tag, a in parse_elements(block) if tag == "a" and a.get("href") == page]
        assert len(more) == 1
        assert more[0].get("data-de") and more[0].get("data-en")
    izzy = fragment(HTML, '<section id="izzy"', "</section>")
    assert "https://github.com/DJTJ9/IzzysIslandParty" in izzy, "„Mehr dazu\" hat den Repo-Link verdrängt"


def test_profile_paragraph_is_the_new_short_profile():
    block = fragment(HTML, '<section id="ueber"', "</section>")
    paras = [a for t, a in parse_elements(block) if t == "p"]
    assert paras, "kein Absatz in der Über-Sektion"
    de, en = paras[0].get("data-de"), paras[0].get("data-en")
    assert de and en, "Kurzprofil ohne vollständiges Sprachpaar"
    assert de.startswith("Sport gilt heute selbstverständlich als wertvoll")
    for term in ["Übung, Feedback, Motivation und Lernen durch Handeln", "Sportwissenschaft",
                 "Datenanalyse", "Engine-Tools", "spielspezifischer KI"]:
        assert term in de, f"Kurzprofil (DE) ohne „{term}\""
    for term in ["practice, feedback, motivation and learning by doing", "sports science",
                 "data analysis", "engine tools", "game-specific AI"]:
        assert term in en, f"Kurzprofil (EN) ohne „{term}\""
    assert "SAE Institute Hamburg (04/2026)" not in de, "alter Hub-Absatz steht noch da"


def test_about_longtext_is_always_visible():
    block = fragment(HTML, '<section id="ueber"', "</section>")
    elements = parse_elements(block)
    assert not any(t in ("details", "summary") for t, _ in elements), \
        "Über mich trägt noch einen Aufklapper"
    subs = [a for t, a in elements if t == "h3" and has_class(a, "about__sub")]
    assert len(subs) == 1, "keine (oder mehrere) Zwischenüberschrift(en) in Über mich"
    assert (subs[0].get("data-de"), subs[0].get("data-en")) == ("Was mich antreibt", "What drives me")
    tail = block[block.index('<h3 class="about__sub"'):]
    paras = [a for t, a in parse_elements(tail) if t == "p"]
    assert len(paras) >= 3, f"nur {len(paras)} Absätze unter „Was mich antreibt\""
    for attrs in paras:
        assert attrs.get("data-de") and attrs.get("data-en")
    assert rules_for_selector(CSS, ".portfolio #ueber p + p"), "Absätze in Über mich kleben aneinander"


def test_about_is_called_ueber_mich_everywhere():
    assert "Wer ich bin" not in HTML and "Who I am" not in HTML
    block = fragment(HTML, '<section id="ueber"', "</section>")
    h2 = [a for t, a in parse_elements(block) if t == "h2"][0]
    assert (h2.get("data-de"), h2.get("data-en")) == ("Über mich", "About me")
    rail = fragment(HTML, '<ol class="rail__scale"', "</ol>")
    labels = [a.get("data-de") for t, a in parse_elements(rail)
              if t == "span" and has_class(a, "rail__label")]
    assert "Über mich" in labels


def test_projects_are_a_visible_group():
    elements = parse_elements(HTML)
    heads = [a for t, a in elements if t == "h2" and a.get("id") == "projekte"]
    assert len(heads) == 1 and not has_class(heads[0], "sr-anchor"), "H2 Projekte ist noch versteckt"
    assert ".sr-anchor" not in CSS, "verwaiste .sr-anchor-Regel"
    intro = [a for t, a in elements if t == "p" and has_class(a, "projects__intro")]
    assert len(intro) == 1 and intro[0].get("data-de") and intro[0].get("data-en")

    rail = fragment(HTML, '<ol class="rail__scale"', "</ol>")
    relems = parse_elements(rail)
    assert len([a for t, a in relems if t == "li" and has_class(a, "rail__group")]) == 1
    glabel = [a for t, a in relems if t == "span" and has_class(a, "rail__group-label")]
    assert glabel and (glabel[0].get("data-de"), glabel[0].get("data-en")) == ("Projekte", "Projects")
    assert not any(t == "a" for t, _ in parse_elements(fragment(rail, '<li class="rail__group"', "</li>"))), \
        "der Gruppenmarker darf kein Link sein"
    assert rail.index('href="#ueber"') < rail.index('class="rail__group"') < rail.index('href="#izzy"')
    assert len([a for t, a in relems if t == "li" and has_class(a, "rail__item--project")]) == 4
    assert rules_for_selector(CSS, ".portfolio .rail__group::after"), "keine Klammer um die Projektgruppe"

    chapters = fragment(HTML, '<nav class="chapters"', "</nav>")
    seps = [a for t, a in parse_elements(chapters) if t == "span" and has_class(a, "chapters__sep")]
    assert len(seps) == 1 and (seps[0].get("data-de"), seps[0].get("data-en")) == ("Projekte:", "Projects:")
    assert chapters.index("chapters__sep") < chapters.index('href="#izzy"')


def test_hero_guides_recruiters_with_two_ctas():
    hero = fragment(HTML, '<section class="hero"', "</section>")
    ctas = [a for t, a in parse_elements(hero) if t == "a" and has_class(a, "cta")]
    assert [a.get("href") for a in ctas] == ["#projekte", "assets/cv/cv-de.pdf"]
    for a in ctas:
        assert a.get("data-de") and a.get("data-en")
    cv = ctas[1]
    assert cv.get("data-href-de") == "assets/cv/cv-de.pdf"
    assert cv.get("data-href-en") == "assets/cv/cv-en.pdf"
    assert "download" in cv
    assert "hrefEn" in JS and "hrefDe" in JS, "applyLang tauscht den CV-Link nicht mit der Sprache"


def test_no_expander_styles_are_left_behind():
    assert ".deeper" not in CSS, "verwaiste Aufklapper-Regeln im Stylesheet"


SKILL_GROUPS = {
    "Engine · täglich": ["Unity", "C#", "Shader"],
    "Game AI · Uni-Projekte": ["Pathfinding", "State Machines", "Behaviour Trees", "GOAP",
                               "Wave Function Collapse"],
    "Werkzeuge · täglich": ["Git", "LLM-Workflows", "MCP"],
    "Grundlagen · angefangen": ["Unreal Engine", "C++"],
    "Mit KI gebaut · läuft produktiv": ["Python", "SQLite", "HTML/CSS", "JavaScript"],
}


def _skill_items():
    skills = fragment(HTML, '<ul class="skills"', "</ul>")
    return [chunk for chunk in re.split(r"<li>", skills)[1:]]


def test_skills_are_five_groups_with_the_level_in_the_label():
    items = _skill_items()
    assert len(items) == 5, f"{len(items)} Skill-Gruppen statt 5"
    seen = {}
    for chunk in items:
        labels = [a for t, a in parse_elements(chunk) if t == "span" and has_class(a, "skills__group")]
        assert len(labels) == 1, "Gruppe ohne genau ein Label"
        assert labels[0].get("data-de") and labels[0].get("data-en"), "Gruppenlabel nicht zweisprachig"
        seen[labels[0]["data-de"]] = text_by_class(chunk, "span", "chip")
    assert seen == SKILL_GROUPS


def test_skills_read_as_a_ladder_and_stack_on_small_screens():
    rows = rules_for_selector(CSS, ".portfolio .skills li")
    assert rows, "keine Regel für .portfolio .skills li"
    assert "grid-template-columns: 220px minmax(0, 1fr)" in rows[0]["body"], \
        "Skill-Zeilen sind nicht zweispaltig"
    label = rules_for_selector(CSS, ".portfolio .skills__group")
    assert label and "text-align: right" in label[0]["body"], "Label-Spalte ist nicht rechtsbündig"
    stacked = rules_for_selector(CSS, ".portfolio .skills li", media="max-width: 640px")
    assert stacked and "grid-template-columns: minmax(0, 1fr)" in stacked[0]["body"], \
        "Skill-Zeilen stapeln unter 640px nicht"


def test_no_tier_colouring_on_the_chips():
    assert not rules_for_selector(CSS, ".portfolio .skills .chip--weak"), \
        "abgewertete Chip-Variante — das Niveau gehört ins Label"
    assert "border-style: dashed" not in CSS


def test_readme_documents_the_about_block_and_the_cv_gate():
    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
    assert "Was mich antreibt" in readme, "README beschreibt den offenen Über-mich-Block nicht"
    assert "Tiefer tauchen" not in readme and "Wer ich bin" not in readme
    assert "master.md" in readme and "test_cv_sync" in readme, \
        "README nennt die CV-Sync-Regel nicht"


def test_skill_chips_flow_inside_one_grid_cell():
    # Regression 2026-09-16: ohne Wrapper wurde jeder Chip zur eigenen Grid-Zelle
    # und die Leiter lief über die volle Breite auseinander.
    for chunk in _skill_items():
        wrappers = [a for t, a in parse_elements(chunk) if t == "span" and has_class(a, "skills__chips")]
        assert len(wrappers) == 1, "Chips einer Gruppe liegen nicht in genau einem Wrapper"
    rules = rules_for_selector(CSS, ".portfolio .skills__chips")
    assert rules, "keine Regel für .portfolio .skills__chips"
    assert "flex-wrap: wrap" in rules[0]["body"], "Chips brechen im Wrapper nicht um"

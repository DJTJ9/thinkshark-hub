from pathlib import Path

from html_utils import fragment, has_class, parse_css_rules, parse_elements, rules_for_selector

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
DETAIL_PAGES = [
    "projekt-izzy.html",
    "projekt-bullseyeq.html",
    "projekt-bob.html",
    "projekt-desk-buddy.html",
]


def _html(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_all_four_detail_pages_exist():
    for name in DETAIL_PAGES:
        assert (ROOT / name).exists(), f"{name} fehlt"


def test_every_detail_page_shares_the_shell():
    for name in DETAIL_PAGES:
        elements = parse_elements(_html(name))
        bodies = [a for t, a in elements if t == "body"]
        assert bodies, f"{name}: kein <body>"
        assert set((bodies[0].get("class") or "").split()) == {"portfolio", "detail"}, \
            f"{name}: falsche body-Klassen"
        assert any(t == "header" and has_class(a, "topbar") for t, a in elements), f"{name}: keine Topbar"
        assert len([a for t, a in elements if t == "button" and has_class(a, "lang__btn")]) == 2, \
            f"{name}: kein vollständiger Sprachumschalter"
        backs = [a for t, a in elements if t == "a" and has_class(a, "detail__back")]
        assert len(backs) == 1 and backs[0].get("href") == "index.html#projekte", \
            f"{name}: kein Zurück-Link auf die Projektliste"
        assert any(t == "footer" and has_class(a, "footer") for t, a in elements), f"{name}: kein Footer"
        assert any(t == "script" and a.get("src") == "main.js" for t, a in elements), f"{name}: main.js fehlt"
        assert not any(t == "nav" and (has_class(a, "rail") or has_class(a, "chapters")) for t, a in elements), \
            f"{name}: Detailseiten tragen keine Sprungnavigation"


def test_every_detail_page_has_three_empty_clip_slots():
    for name in DETAIL_PAGES:
        figs = [a for t, a in parse_elements(_html(name)) if t == "figure" and has_class(a, "clip")]
        assert len(figs) == 3, f"{name}: {len(figs)} Clip-Slots statt 3"
        assert all(has_class(a, "clip--empty") for a in figs), \
            f"{name}: ein Clip-Slot ist nicht als leer markiert"


def test_every_detail_page_has_a_role_section():
    for name in DETAIL_PAGES:
        html = _html(name)
        assert 'data-de="Meine Rolle"' in html and 'data-en="My role"' in html, \
            f"{name}: kein Abschnitt „Meine Rolle\""


def test_every_detail_page_is_bilingual():
    for name in DETAIL_PAGES:
        nodes = [a for _, a in parse_elements(_html(name)) if "data-de" in a or "data-en" in a]
        assert len(nodes) >= 6, f"{name}: zu wenige übersetzbare Knoten"
        for attrs in nodes:
            assert attrs.get("data-de") and attrs.get("data-en"), f"{name}: unvollständiges Sprachpaar {attrs}"


def test_detail_pages_have_their_own_title_and_description():
    titles = set()
    for name in DETAIL_PAGES:
        html = _html(name)
        title = fragment(html, "<title>", "</title>")
        assert "noindex" not in html, f"{name}: Detailseiten sollen crawlbar sein"
        descs = [a for t, a in parse_elements(html) if t == "meta" and a.get("name") == "description"]
        assert descs and descs[0].get("content"), f"{name}: keine Meta-Description"
        titles.add(title)
    assert len(titles) == 4, "Detailseiten teilen sich Titel"


def test_desk_buddy_detail_keeps_wip_badge_and_no_repo_link():
    html = _html("projekt-desk-buddy.html")
    assert any(has_class(a, "badge--wip") for _, a in parse_elements(html)), "kein WIP-Badge"
    assert "github.com" not in html, "Desk-Buddy darf keinen Repo-Link haben"


def test_repo_links_on_the_other_three_detail_pages():
    expected = {
        "projekt-izzy.html": "https://github.com/DJTJ9/IzzysIslandParty",
        "projekt-bullseyeq.html": "https://github.com/DJTJ9/BullseyeQ",
        "projekt-bob.html": "https://github.com/DJTJ9/job-scanner",
    }
    for name, url in expected.items():
        hrefs = {a.get("href") for t, a in parse_elements(_html(name)) if t == "a"}
        assert url in hrefs, f"{name}: Repo-Link {url} fehlt"


def test_detail_rules_are_scoped_to_the_detail_body_class():
    unscoped = []
    for rule in parse_css_rules(CSS):
        for sel in rule["selectors"]:
            if ("detail__" in sel or ".clip" in sel) and not sel.startswith(".detail"):
                unscoped.append(sel)
    assert not unscoped, "ungescopte Detailseiten-Regeln: " + ", ".join(unscoped)


def test_empty_clip_slot_keeps_a_16_by_9_box():
    rules = rules_for_selector(CSS, ".detail .clip--empty")
    assert rules, "keine Regel für .detail .clip--empty"
    assert "aspect-ratio: 16 / 9" in rules[0]["body"]

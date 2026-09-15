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


LONGTEXT_HEADINGS = [
    ('data-de="Worum es geht"', 'data-en="What it is"'),
    ('data-de="Worauf ich stolz bin"', 'data-en="What I am proud of"'),
    ('data-de="Woran ich hängen geblieben bin"', 'data-en="Where I got stuck"'),
    ('data-de="Meine Rolle"', 'data-en="My role"'),
]


def test_every_detail_page_carries_the_four_longtext_blocks():
    for name in DETAIL_PAGES:
        html = _html(name)
        for de_attr, en_attr in LONGTEXT_HEADINGS:
            assert de_attr in html and en_attr in html, f"{name}: Block {de_attr} fehlt"
        assert "Text folgt." not in html and "Text coming." not in html, \
            f"{name}: Platzhaltertext steht noch drin"


def _longtext(name):
    html = _html(name)
    body = html[html.index('data-de="Worum es geht"'):]
    # der nachgestellte Repo-Link steht in einem eigenen, unuebersetzten <p>
    if '<p><a class="project__link"' in body:
        body = body[:body.index('<p><a class="project__link"')]
    return body


def test_longtexts_are_substantial_and_bilingual():
    for name in DETAIL_PAGES:
        paras = [a for t, a in parse_elements(_longtext(name)) if t == "p"]
        assert len(paras) >= 6, f"{name}: nur {len(paras)} Langtext-Absätze"
        for attrs in paras:
            de, en = attrs.get("data-de"), attrs.get("data-en")
            assert de and en, f"{name}: Langtext-Absatz ohne Sprachpaar"
            assert len(de) > 120, f"{name}: Langtext-Absatz zu kurz ({len(de)} Zeichen)"


def test_izzy_splits_the_three_games_into_expanders():
    body = _longtext("projekt-izzy.html")
    elements = parse_elements(body)
    details = [a for t, a in elements if t == "details" and has_class(a, "deeper")]
    assert len(details) == 3, f"{len(details)} Aufklapper statt einer je Spiel"
    assert all("open" not in a for a in details), "ein Spiel-Aufklapper ist im Markup schon geöffnet"
    summaries = [a.get("data-de") for t, a in elements if t == "summary"]
    assert summaries == ["Minigolf Mayhem", "Swaggy Snapshots", "Bowling Battle"], \
        f"unerwartete Spielnamen: {summaries}"
    assert 'data-de="Die gemeinsame Basis"' in body, "der gemeinsame UI-/Event-Unterbau fehlt"


def test_the_ai_share_is_named_on_every_project():
    # Entscheidung 2026-09-16: Izzy ist ohne KI entstanden, die drei anderen mit.
    izzy = _longtext("projekt-izzy.html")
    assert "ohne Coding-Agents" in izzy, "Izzy benennt die Eigenarbeit ohne KI nicht"
    for name in ("projekt-bullseyeq.html", "projekt-bob.html", "projekt-desk-buddy.html"):
        body = _longtext(name)
        assert "Coding Agent" in body or "mit KI" in body or "Die KI" in body, \
            f"{name}: der KI-Anteil wird nicht benannt"


def test_longtext_paragraphs_and_headings_keep_their_spacing():
    # Regression 2026-09-16: .portfolio p traegt keinen Margin — ohne diese Regeln
    # kleben aufeinanderfolgende Absaetze und Ueberschriften aneinander.
    paras = rules_for_selector(CSS, ".detail main p + p")
    assert paras and "margin-top" in paras[0]["body"], "aufeinanderfolgende Absätze ohne Abstand"
    heads = rules_for_selector(CSS, ".detail main h2")
    assert heads and "margin-top" in heads[0]["body"], "Abschnittsüberschriften ohne Abstand nach oben"
    sub = rules_for_selector(CSS, ".portfolio .deeper h3")
    assert sub and "margin-top" in sub[0]["body"], "Spiel-Zwischenüberschriften ohne Abstand"

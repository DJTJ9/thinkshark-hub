from pathlib import Path

from html_utils import fragment, has_class, parse_css_rules, parse_elements, rules_for_selector, text_by_class

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


def test_clip_video_keeps_a_16_by_9_box():
    rules = rules_for_selector(CSS, ".detail .clip video")
    assert rules and "aspect-ratio: 16 / 9" in rules[0]["body"] and "height: auto" in rules[0]["body"]


LONGTEXT_HEADINGS = [
    ('data-de="Worum es geht"', 'data-en="What it is"'),
    ('data-de="Worauf ich stolz bin"', 'data-en="What I am proud of"'),
    ('data-de="Woran ich hängen geblieben bin"', 'data-en="Where I got stuck"'),
]


def test_every_detail_page_carries_the_three_longtext_blocks():
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
    sub = rules_for_selector(CSS, ".detail .game h3")
    assert sub and "margin-top" in sub[0]["body"], "Spiel-Zwischenüberschriften ohne Abstand"


NEXT_PROJECT = {
    "projekt-izzy.html": ("projekt-bullseyeq.html", "BullseyeQ"),
    "projekt-bullseyeq.html": ("projekt-bob.html", "Bob der Job-Bot"),
    "projekt-bob.html": ("projekt-desk-buddy.html", "Desk-Buddy"),
    "projekt-desk-buddy.html": ("projekt-izzy.html", "Izzy's Island Party"),
}


def test_only_izzy_carries_clip_slots():
    for name in DETAIL_PAGES:
        figs = [a for t, a in parse_elements(_html(name)) if t == "figure" and has_class(a, "clip")]
        expected = 3 if name == "projekt-izzy.html" else 0
        assert len(figs) == expected, f"{name}: {len(figs)} Clip-Slots statt {expected}"


CLIPS = ["minigolf", "swaggy", "bowling"]


def test_izzy_clips_are_lazy_muted_loops():
    html = _html("projekt-izzy.html")
    elements = parse_elements(html)
    videos = [a for t, a in elements if t == "video"]
    assert [a.get("poster") for a in videos] == [f"assets/clips/{n}.jpg" for n in CLIPS]
    for a in videos:
        for flag in ("muted", "loop", "playsinline"):
            assert flag in a, f"Clip ohne {flag}"
        assert a.get("preload") == "none", "Clips laden schon beim Seitenaufruf"
        assert "autoplay" not in a and "controls" not in a, "Abspielen steuert main.js"
        assert (a.get("width"), a.get("height")) == ("1280", "720"), "Layout-Shift: width/height fehlen"
    sources = [a for t, a in elements if t == "source"]
    assert [(a.get("src"), a.get("type")) for a in sources] == [(f"assets/clips/{n}.mp4", "video/mp4") for n in CLIPS]
    for name in DETAIL_PAGES:
        assert "clip--empty" not in _html(name) and "Clip folgt" not in _html(name)
    assert ".clip--empty" not in CSS
    js = (ROOT / "main.js").read_text(encoding="utf-8")
    assert ".clip video" in js and ".play()" in js and ".pause()" in js and "controls = true" in js


def test_role_is_folded_into_the_summary():
    for name in DETAIL_PAGES:
        html = _html(name)
        assert "Meine Rolle" not in html and "My role" not in html, f"{name}: eigener Rollen-Abschnitt steht noch"
        summary = html[html.index('data-de="Worum es geht"'):]
        summary = summary[:summary.index("<h2", 10)]
        paras = [a for t, a in parse_elements(summary) if t == "p"]
        assert len(paras) >= 3, f"{name}: Rolle ist nicht in „Worum es geht\" angekommen"


def test_izzy_shows_the_three_games_as_open_blocks():
    html = _html("projekt-izzy.html")
    elements = parse_elements(html)
    assert not any(t in ("details", "summary") for t, _ in elements), "Izzy trägt noch Aufklapper"
    games = [a for t, a in elements if t == "article" and has_class(a, "game")]
    assert len(games) == 3
    sides = ["game--left" if has_class(a, "game--left") else "game--right" for a in games]
    assert sides == ["game--left", "game--right", "game--left"], "Clips alternieren nicht"
    assert text_by_class(html, "h2", "game__title") == ["Minigolf Mayhem", "Swaggy Snapshots", "Bowling Battle"]
    for chunk in html.split('<article class="game')[1:]:
        block = chunk[:chunk.index("</article>")]
        figs = [a for t, a in parse_elements(block) if t == "figure" and has_class(a, "clip")]
        assert len(figs) == 1, "Spielblock ohne genau einen Clip"
    assert 'data-de="Die gemeinsame Basis"' in html
    stacked = rules_for_selector(CSS, ".detail .game", media="max-width: 760px")
    assert stacked and "grid-template-columns: minmax(0, 1fr)" in stacked[0]["body"]


def test_every_detail_page_ends_with_next_project_and_contact():
    for name, (target, label) in NEXT_PROJECT.items():
        html = _html(name)
        nav = fragment(html, '<nav class="detail__next"', "</nav>")
        links = [a for t, a in parse_elements(nav) if t == "a" and has_class(a, "detail__next-link")]
        assert [a.get("href") for a in links] == [target, "index.html#kontakt"], f"{name}: falsche Fußnavigation"
        assert links[0].get("data-de") == f"Nächstes Projekt: {label}"
        assert links[0].get("data-en") == f"Next project: {label}"
        assert (links[1].get("data-de"), links[1].get("data-en")) == ("Kontakt", "Contact")

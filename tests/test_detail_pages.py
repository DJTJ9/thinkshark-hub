from pathlib import Path

import pytest
from html_utils import DIST, fragment, has_class, parse_css_rules, parse_elements, rules_for_selector, text_by_class

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
DETAIL_PAGES = [
    "projekt-izzy.html",
    "projekt-bullseyeq.html",
    "projekt-bob.html",
    "projekt-desk-buddy.html",
]


def _html(name):
    return (DIST / name).read_text(encoding="utf-8")


def test_all_four_detail_pages_exist():
    for name in DETAIL_PAGES:
        assert (DIST / name).exists(), f"{name} fehlt"


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


# Gate 2026-09-27: jede Detailseite erzählt Idee → Worum es geht → Highlights & Herausforderungen.
LONGTEXT_HEADINGS = [
    ("Die Idee", "The idea"),
    ("Worum es geht", "What it is"),
    ("Highlights & Herausforderungen", "Highlights & challenges"),
]
RETIRED_HEADINGS = ["Worauf ich stolz bin", "What I am proud of", "Woran ich hängen geblieben bin", "Where I got stuck"]


def _headings(html, *tags):
    """(tag, data-de, data-en) aller übersetzten Überschriften in Dokumentreihenfolge."""
    return [(t, a.get("data-de"), a.get("data-en")) for t, a in parse_elements(html)
            if t in tags and "data-de" in a]


@pytest.mark.parametrize("name", DETAIL_PAGES)
def test_every_detail_page_carries_the_three_longtext_blocks(name):
    html = _html(name)
    heads = [(de, en) for _, de, en in _headings(html, "h2", "h3")]
    for pair in LONGTEXT_HEADINGS:
        assert pair in heads, f"{name}: Überschriftenpaar {pair} fehlt"
    for old in RETIRED_HEADINGS:
        assert old not in html, f"{name}: alte Überschrift „{old}“ steht noch drin"
    assert "Text folgt." not in html and "Text coming." not in html, \
        f"{name}: Platzhaltertext steht noch drin"


@pytest.mark.parametrize("name", DETAIL_PAGES)
def test_the_idea_opens_every_detail_page(name):
    heads = _headings(_html(name), "h2", "h3", "h4")
    assert heads[0] == ("h2", "Die Idee", "The idea"), f"{name}: erste Überschrift ist {heads[0]}"
    if name == "projekt-izzy.html":
        return
    order = [(t, de) for t, de, _ in heads if de in {p[0] for p in LONGTEXT_HEADINGS}]
    assert order == [("h2", de) for de, _ in LONGTEXT_HEADINGS], f"{name}: Abschnittsfolge {order}"
    after = [t for t, _, _ in heads[heads.index(("h2", "Highlights & Herausforderungen", "Highlights & challenges")) + 1:]]
    assert after and after[0] == "h3", f"{name}: Highlights ohne h3-Unterabschnitte"


def test_izzy_games_follow_the_same_scheme_one_level_deeper():
    html = _html("projekt-izzy.html")
    for chunk in html.split('<article class="game')[1:]:
        heads = _headings(chunk[:chunk.index("</article>")], "h3", "h4")
        h3 = [(de, en) for t, de, en in heads if t == "h3"]
        assert h3 == LONGTEXT_HEADINGS[1:], f"Spielblock-h3 sind {h3}"
        tail = heads[[de for _, de, _ in heads].index("Highlights & Herausforderungen") + 1:]
        assert tail and all(t == "h4" for t, _, _ in tail), "Highlights im Spielblock ohne h4-Unterabschnitte"


def _longtext(name):
    html = _html(name)
    body = html[html.index('data-de="Die Idee"'):]
    # der nachgestellte Repo-Link steht in einem eigenen, unuebersetzten <p>
    if '<p><a class="project__link"' in body:
        body = body[:body.index('<p><a class="project__link"')]
    return body


@pytest.mark.parametrize("name", DETAIL_PAGES)
def test_longtexts_are_substantial_and_bilingual(name):
    paras = [a for t, a in parse_elements(_longtext(name)) if t == "p"]
    assert len(paras) >= 6, f"{name}: nur {len(paras)} Langtext-Absätze"
    for attrs in paras:
        de, en = attrs.get("data-de"), attrs.get("data-en")
        assert de and en, f"{name}: Langtext-Absatz ohne Sprachpaar"
        assert len(de) > 120, f"{name}: Langtext-Absatz zu kurz ({len(de)} Zeichen)"


@pytest.mark.parametrize("name", DETAIL_PAGES)
def test_the_ai_share_is_named_on_every_project(name):
    # Entscheidung 2026-09-16: Izzy ist ohne KI entstanden, die drei anderen mit.
    body = _longtext(name)
    if name == "projekt-izzy.html":
        assert "ohne Coding-Agents" in body, "Izzy benennt die Eigenarbeit ohne KI nicht"
    else:
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
    # Gate 2026-09-27: Highlight-Unterabschnitte als h3 (Seite) bzw. h4 (Izzy-Spielblock)
    for sel in (".detail main h3", ".detail main h4"):
        rules = rules_for_selector(CSS, sel)
        assert rules and "margin-top" in rules[0]["body"] and "font-family" in rules[0]["body"], \
            f"{sel} ungestylt"


NEXT_PROJECT = {
    "projekt-izzy.html": ("projekt-bullseyeq.html", "BullseyeQ"),
    "projekt-bullseyeq.html": ("projekt-bob.html", "Bob der Job-Bot"),
    "projekt-bob.html": ("projekt-desk-buddy.html", "Desk-Buddy"),
    "projekt-desk-buddy.html": ("projekt-izzy.html", "Izzy's Island Party"),
}


def test_only_izzy_carries_video_clips():
    for name in DETAIL_PAGES:
        videos = [a for t, a in parse_elements(_html(name)) if t == "video"]
        expected = 3 if name == "projekt-izzy.html" else 0
        assert len(videos) == expected, f"{name}: {len(videos)} Videos statt {expected}"


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


@pytest.mark.parametrize("name", DETAIL_PAGES)
def test_role_is_folded_into_the_summary(name):
    # Gate 2026-09-27: die Rolle steht im Überblick — bei Izzy in „Die Idee“
    # (Aufteilung im Team), sonst in „Worum es geht“.
    html = _html(name)
    assert "Meine Rolle" not in html and "My role" not in html, f"{name}: eigener Rollen-Abschnitt steht noch"
    heading = "Die Idee" if name == "projekt-izzy.html" else "Worum es geht"
    summary = html[html.index(f'data-de="{heading}"'):]
    summary = summary[:summary.index("<h2", 10)]
    paras = [a for t, a in parse_elements(summary) if t == "p"]
    assert len(paras) >= 3, f"{name}: Rolle ist nicht in „{heading}\" angekommen"


def test_bob_opens_with_the_idea_and_closes_with_the_roadmap():
    html = _html("projekt-bob.html")
    order = [html.index(s) for s in (
        'class="detail__intro"', 'data-de="Die Idee"', 'data-de="Worum es geht"',
        'data-de="Highlights &amp; Herausforderungen"', 'data-de="Roadmap"', '<p><a class="project__link"')]
    assert order == sorted(order), "Bob: Abschnitts-Reihenfolge stimmt nicht"
    assert 'data-en="The idea"' in html and 'data-en="Roadmap"' in html
    # Entscheidung 2026-09-20: keine Embedding-Suche im Code, also auch nicht im Text.
    assert "semantisch" not in html.lower() and "semantic" not in html.lower()
    assert "invite" not in html.lower() and "einladungscode" not in html.lower()


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


def test_bullseyeq_shows_four_to_five_captioned_screenshots():
    elements = parse_elements(_html("projekt-bullseyeq.html"))
    imgs = [a for t, a in elements if t == "img"]
    assert 4 <= len(imgs) <= 5, f"{len(imgs)} Screenshots statt 4–5"
    for a in imgs:
        src = a.get("src") or ""
        assert src.startswith("assets/projects/bullseyeq-") and src.endswith(".webp"), src
        assert (ROOT / src).exists(), f"fehlt: {src}"
        assert a.get("alt") and a.get("data-alt-de") and a.get("data-alt-en"), f"{src}: Alt-Paar fehlt"
        assert a.get("alt") == a.get("data-alt-de")
        assert a.get("loading") == "lazy" and (a.get("width"), a.get("height")) == ("1280", "720")
    captions = [a for t, a in elements if t == "figcaption"]
    assert len(captions) == len(imgs), "jeder Shot braucht eine figcaption"
    assert all(c.get("data-de") and c.get("data-en") for c in captions)


def test_bullseyeq_credits_the_ui_asset_pack():
    body = _longtext("projekt-bullseyeq.html")
    assert "Layer Lab" in body, "Asset-Credit fehlt"


def test_highlight_blocks_with_an_image_match_the_plain_subsections():
    # 2026-09-27: BullseyeQ mischt h3-Unterabschnitte mit Bild (div.game) und ohne.
    # Beide tragen dieselbe Schriftgröße und denselben Abstand; der erste Block
    # klebt nicht 56px unter der Abschnittsüberschrift.
    first = rules_for_selector(CSS, ".detail main h2 + .game")
    assert first and "margin-top: 24px" in first[0]["body"], "erster Bildblock zu weit unter dem h2"
    size = rules_for_selector(CSS, ".detail div.game h3")
    plain = rules_for_selector(CSS, ".detail main h3")
    assert size and "font-size: 1.25rem" in size[0]["body"] and "font-size: 1.25rem" in plain[0]["body"], \
        "h3 mit und ohne Bild sind unterschiedlich groß"
    after = rules_for_selector(CSS, ".detail main .game + h3")
    assert after and "margin-top: 56px" in after[0]["body"], "h3 nach einem Bildblock ohne Blockabstand"


def test_clip_images_keep_their_ratio():
    rules = rules_for_selector(CSS, ".detail .clip img")
    assert rules and "height: auto" in rules[0]["body"], ".clip img ohne height: auto"


def test_image_alt_follows_the_language_switch():
    js = (ROOT / "main.js").read_text(encoding="utf-8")
    assert "[data-alt-de][data-alt-en]" in js
    assert "el.alt =" in js


def test_bullseyeq_detail_links_the_browser_build():
    links = [a for t, a in parse_elements(_html("projekt-bullseyeq.html"))
             if t == "a" and a.get("href") == "https://darts.thinkshark.de"]
    assert len(links) == 1, "Link auf darts.thinkshark.de fehlt"
    link = links[0]
    assert has_class(link, "project__link")
    assert link.get("target") == "_blank" and link.get("rel") == "noopener"
    assert link.get("data-de") == "Im Browser testen"
    assert link.get("data-en") == "Try it in the browser"

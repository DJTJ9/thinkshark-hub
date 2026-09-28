"""build.py: Vorlagen + content/*.md → dist/. Jeder Content-Fehler bricht hart ab."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402

TEMPLATE = """<!doctype html>
<html lang="de">
<head>
  <title></title>
  <meta name="description" content="" />
  <meta property="og:title" content="" />
  <meta property="og:description" content="" />
</head>
<body>
  <h1 data-t="p.title"></h1>
  <a class="cta" data-t-href="p.cv.href" download data-t="p.cv"></a>
  <img src="x.png" data-t-alt="p.shot.alt" />
</body>
</html>
"""
DE = """---
title: Seite | Tjark
description: Beschreibung & mehr
---

## p.title
Hallo "Welt"
und Meer

## p.cv
CV laden

## p.cv.href
assets/cv/cv-de.pdf

## p.shot.alt
Bild A & B
"""
EN = """## p.title
Hello world

## p.cv
Download CV

## p.cv.href
assets/cv/cv-en.pdf

## p.shot.alt
Picture A & B
"""


def _site(tmp_path, template=TEMPLATE, de=DE, en=EN):
    (tmp_path / "templates").mkdir()
    (tmp_path / "content").mkdir()
    (tmp_path / "templates" / "p.html").write_text(template, encoding="utf-8")
    (tmp_path / "content" / "p.de.md").write_text(de, encoding="utf-8")
    (tmp_path / "content" / "p.en.md").write_text(en, encoding="utf-8")
    return tmp_path


def _build(root):
    build.build(root, root / "dist", static=())
    return (root / "dist" / "p.html").read_text(encoding="utf-8")


def _fails(tmp_path, match, **kw):
    root = _site(tmp_path, **kw)
    with pytest.raises(build.BuildError, match=match):
        build.build(root, root / "dist", static=())


def test_parse_content_joins_lines_and_reads_front_matter(tmp_path):
    p = tmp_path / "p.de.md"
    p.write_text(DE, encoding="utf-8")
    meta, blocks = build.parse_content(p)
    assert meta == {"title": "Seite | Tjark", "description": "Beschreibung & mehr"}
    assert blocks["p.title"] == 'Hallo "Welt" und Meer'
    assert list(blocks) == ["p.title", "p.cv", "p.cv.href", "p.shot.alt"]


def test_fills_text_keys_with_both_languages(tmp_path):
    out = _build(_site(tmp_path))
    assert '<h1 data-de="Hallo &quot;Welt&quot; und Meer" data-en="Hello world">Hallo "Welt" und Meer</h1>' in out


def test_fills_alt_and_href_keys(tmp_path):
    out = _build(_site(tmp_path))
    assert ('href="assets/cv/cv-de.pdf" data-href-de="assets/cv/cv-de.pdf" '
            'data-href-en="assets/cv/cv-en.pdf" download data-de="CV laden" data-en="Download CV">CV laden</a>') in out
    assert 'alt="Bild A &amp; B" data-alt-de="Bild A &amp; B" data-alt-en="Picture A &amp; B"' in out


def test_fills_title_and_meta_from_front_matter(tmp_path):
    out = _build(_site(tmp_path))
    assert "<title>Seite | Tjark</title>" in out
    assert '<meta name="description" content="Beschreibung &amp; mehr" />' in out
    assert '<meta property="og:title" content="Seite | Tjark" />' in out
    assert '<meta property="og:description" content="Beschreibung &amp; mehr" />' in out


def test_no_marker_survives(tmp_path):
    out = _build(_site(tmp_path))
    assert "data-t" not in out


def test_copies_static_whitelist(tmp_path):
    root = _site(tmp_path)
    (root / "styles.css").write_text("body{}", encoding="utf-8")
    (root / "fonts").mkdir()
    (root / "fonts" / "a.woff2").write_bytes(b"x")
    build.build(root, root / "dist", static=("styles.css", "fonts"))
    assert (root / "dist" / "styles.css").exists()
    assert (root / "dist" / "fonts" / "a.woff2").exists()


def test_missing_static_file_fails(tmp_path):
    root = _site(tmp_path)
    with pytest.raises(build.BuildError, match="statische Datei fehlt: styles.css"):
        build.build(root, root / "dist", static=("styles.css",))


def test_rebuild_removes_stale_files(tmp_path):
    root = _site(tmp_path)
    (root / "dist").mkdir()
    (root / "dist" / "alt.html").write_text("x", encoding="utf-8")
    _build(root)
    assert not (root / "dist" / "alt.html").exists()


def test_key_missing_in_en_fails(tmp_path):
    _fails(tmp_path, r"'p\.title' fehlt in p\.en\.md", en=EN.replace("## p.title\nHello world\n", ""))


def test_key_missing_in_both_fails(tmp_path):
    _fails(tmp_path, r"'p\.neu' fehlt in p\.de\.md, p\.en\.md",
           template=TEMPLATE.replace("</body>", '<p data-t="p.neu"></p></body>'))


def test_orphan_key_fails(tmp_path):
    _fails(tmp_path, r"verwaiste Schlüssel in p\.de\.md: p\.alt", de=DE + "\n## p.alt\nweg\n")


def test_duplicate_key_fails(tmp_path):
    _fails(tmp_path, r"p\.de\.md: Schlüssel 'p\.cv' doppelt", de=DE + "\n## p.cv\nnochmal\n")


def test_empty_block_fails(tmp_path):
    _fails(tmp_path, r"p\.en\.md: Schlüssel 'p\.cv' ohne Text",
           en=EN.replace("## p.cv\nDownload CV\n", "## p.cv\n\n"))


def test_text_before_first_key_fails(tmp_path):
    _fails(tmp_path, r"p\.en\.md: Text vor dem ersten", en="lose Zeile\n" + EN)


def test_front_matter_in_en_fails(tmp_path):
    _fails(tmp_path, r"Front-Matter nur in p\.de\.md", en="---\ntitle: X\n---\n" + EN)


def test_missing_front_matter_field_fails(tmp_path):
    _fails(tmp_path, r"Front-Matter 'description' fehlt in p\.de\.md",
           de=DE.replace("description: Beschreibung & mehr\n", ""))


def test_unknown_front_matter_field_fails(tmp_path):
    _fails(tmp_path, r"unbekanntes Front-Matter-Feld 'autor'", de=DE.replace("---\n\n", "autor: T\n---\n\n", 1))


def test_template_without_meta_tag_fails(tmp_path):
    _fails(tmp_path, r"Vorlage ohne <meta property=\"og:title\"",
           template=TEMPLATE.replace('  <meta property="og:title" content="" />\n', ""))


def test_marker_on_element_with_children_fails(tmp_path):
    _fails(tmp_path, r"data-t=\"p\.title\" darf nur Text enthalten",
           template=TEMPLATE.replace('<h1 data-t="p.title"></h1>', '<h1 data-t="p.title"><b>x</b></h1>'))


def test_content_without_template_fails(tmp_path):
    root = _site(tmp_path)
    (root / "content" / "weg.de.md").write_text("## a\nb\n", encoding="utf-8")
    with pytest.raises(build.BuildError, match=r"content/weg\.de\.md ohne Vorlage"):
        build.build(root, root / "dist", static=())


def test_failed_build_keeps_old_dist(tmp_path):
    root = _site(tmp_path, en="")
    (root / "dist").mkdir()
    (root / "dist" / "live.html").write_text("alt", encoding="utf-8")
    with pytest.raises(build.BuildError):
        build.build(root, root / "dist", static=())
    assert (root / "dist" / "live.html").exists()


PAGES = ["index.html", "projekt-izzy.html", "projekt-bullseyeq.html", "projekt-bob.html", "projekt-desk-buddy.html"]


def test_real_site_builds(tmp_path):
    root = Path(build.__file__).resolve().parent
    assert build.build(root, tmp_path / "dist") == sorted(PAGES)
    for name in PAGES:
        page = (tmp_path / "dist" / name).read_text(encoding="utf-8")
        assert "data-t" not in page and "data-de=" in page
    for item in build.STATIC:
        assert (tmp_path / "dist" / item).exists(), item


def test_pages_live_only_as_templates():
    root = Path(build.__file__).resolve().parent
    for name in PAGES:
        assert not (root / name).exists(), f"{name} liegt noch im Root, gehört nach templates/"

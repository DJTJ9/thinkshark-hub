"""Migration: data-de/data-en → Vorlage + Markdown, Build muss DOM-gleich zurückführen. Temporär."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402
import extract_content as ex  # noqa: E402

PAGE = """<!doctype html>
<html lang="de">
<head>
  <title>Izzy &amp; Co | Tjark</title>
  <meta name="description" content="Beschreibung: lang" />
  <meta property="og:title" content="Izzy &amp; Co | Tjark" />
  <meta property="og:description" content="Beschreibung: lang" />
</head>
<body>
  <header class="topbar"><a href="index.html" data-de="Zurück" data-en="Back">Zurück</a></header>
  <main class="wrap">
    <section id="ueber">
      <p class="x"
         data-de="Ein langer
                  Absatz &amp; mehr"
         data-en="A long paragraph &amp; more">Ein langer
                  Absatz &amp; mehr</p>
      <a class="cta" href="a-de.pdf" data-href-de="a-de.pdf" data-href-en="a-en.pdf" download data-de="CV laden" data-en="Download CV">CV laden</a>
    </section>
    <article class="game game--left"><h3 data-de="Highlights &amp; Herausforderungen" data-en="Highlights &amp; challenges">Highlights &amp; Herausforderungen</h3></article>
    <article class="game game--right"><img src="s.png" alt="Bild" data-alt-de="Bild" data-alt-en="Picture" /></article>
  </main>
</body>
</html>
"""


def _extract():
    return ex.extract(PAGE, "izzy")


def test_keys_are_named_after_their_section():
    _, _, de, en = _extract()
    assert list(de) == ["izzy.topbar.1", "izzy.ueber.1", "izzy.ueber.2", "izzy.ueber.2.href",
                        "izzy.game1.1", "izzy.game2.1.alt"]
    assert de["izzy.ueber.1"] == "Ein langer Absatz & mehr"
    assert en["izzy.ueber.2.href"] == "a-en.pdf"
    assert en["izzy.game2.1.alt"] == "Picture"


def test_template_carries_only_keys():
    tpl, meta, _, _ = _extract()
    assert "data-de" not in tpl and "data-alt-de" not in tpl and "data-href-de" not in tpl
    assert '<p class="x"\n         data-t="izzy.ueber.1"></p>' in tpl
    assert '<a class="cta" data-t-href="izzy.ueber.2.href" download data-t="izzy.ueber.2"></a>' in tpl
    assert '<img src="s.png" data-t-alt="izzy.game2.1.alt" />' in tpl
    assert "<title></title>" in tpl and '<meta property="og:title" content="" />' in tpl
    assert meta == {"title": "Izzy & Co | Tjark", "description": "Beschreibung: lang"}


def test_round_trip_is_dom_equal(tmp_path):
    tpl, meta, de, en = _extract()
    (tmp_path / "templates").mkdir()
    (tmp_path / "content").mkdir()
    (tmp_path / "templates" / "p.html").write_text(tpl, encoding="utf-8")
    (tmp_path / "content" / "p.de.md").write_text(ex.to_markdown(de, meta), encoding="utf-8")
    (tmp_path / "content" / "p.en.md").write_text(ex.to_markdown(en), encoding="utf-8")
    build.build(tmp_path, tmp_path / "dist", static=())
    base = tmp_path / "base"
    base.mkdir()
    (base / "p.html").write_text(PAGE, encoding="utf-8")
    assert ex.verify(base, tmp_path / "dist", pages=["p.html"]) == []


def test_verify_reports_a_changed_text(tmp_path):
    for d, text in (("a", "<p>Hallo</p>"), ("b", "<p>Hallo Welt</p>")):
        (tmp_path / d).mkdir()
        (tmp_path / d / "p.html").write_text(text, encoding="utf-8")
    diffs = ex.verify(tmp_path / "a", tmp_path / "b", pages=["p.html"])
    assert len(diffs) == 1 and "p.html" in diffs[0]


def test_markdown_wraps_long_text_and_parses_back(tmp_path):
    text = "wort " * 60
    md = ex.to_markdown({"k.1": text.strip()}, {"title": "T", "description": "D"})
    assert md.startswith("---\ntitle: T\ndescription: D\n---\n")
    assert max(len(line) for line in md.splitlines()) <= 100
    p = tmp_path / "x.de.md"
    p.write_text(md, encoding="utf-8")
    assert build.parse_content(p)[1] == {"k.1": text.strip()}

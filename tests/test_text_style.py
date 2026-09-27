"""Stilregel (Tjark, 2026-09-27): keine Gedankenstriche, Bis-Striche und Semikolons in Seitentexten."""
from html.parser import HTMLParser
from pathlib import Path

import pytest
from html_utils import parse_elements

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(p.name for p in ROOT.glob("*.html"))
ATTRS = ("data-de", "data-en", "alt", "data-alt-de", "data-alt-en", "aria-label", "title", "content")
FORBIDDEN = {"—": "Gedankenstrich", "–": "Bis-Strich", ";": "Semikolon"}


class _VisibleText(HTMLParser):
    """Textknoten außerhalb von <script> und <style>, Entities aufgelöst."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.out.append(" ".join(data.split()))


def _texts(html):
    parser = _VisibleText()
    parser.feed(html)
    yield from (("Text", t) for t in parser.out)
    for tag, attrs in parse_elements(html):
        yield from ((f"<{tag} {a}>", attrs[a]) for a in ATTRS if attrs.get(a))


def test_all_pages_are_checked():
    assert len(PAGES) >= 9, PAGES


@pytest.mark.parametrize("name", PAGES)
def test_no_dashes_or_semicolons(name):
    html = (ROOT / name).read_text(encoding="utf-8")
    hits = [f"{FORBIDDEN[c]} in {where}: {text[:90]}"
            for where, text in _texts(html) for c in FORBIDDEN if c in text]
    assert not hits, f"{name}:\n" + "\n".join(hits)


@pytest.mark.parametrize("name", PAGES)
def test_no_control_characters(name):
    html = (ROOT / name).read_text(encoding="utf-8")
    bad = sorted({hex(ord(c)) for c in html if ord(c) < 32 and c not in "\n\r\t"})
    assert not bad, f"{name}: Steuerzeichen {bad}"

"""Prüft, dass jeder lokale href/src auf den fünf Seiten wirklich existiert.

Deckt eine Lücke, die die übrige Suite (reines String-Matching) nicht sieht:
ein kaputter relativer Link/Pfad faellt sonst nirgends auf.
"""
from urllib.parse import urlsplit

from html_utils import DIST, parse_elements

PAGES = [
    "index.html", "hub.html", "impressum.html", "datenschutz.html", "changelog.html",
    "projekt-izzy.html", "projekt-bullseyeq.html", "projekt-bob.html", "projekt-desk-buddy.html",
]

ATTR_BY_TAG = {"a": "href", "link": "href", "script": "src", "img": "src", "source": "src", "video": "poster"}


def _local_targets(html_text):
    targets = []
    for tag, attrs in parse_elements(html_text):
        attr = ATTR_BY_TAG.get(tag)
        if not attr:
            continue
        value = attrs.get(attr)
        if not value:
            continue
        if value.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = urlsplit(value).path  # Fragment/Query abschneiden
        if not path:
            continue
        targets.append(path)
    return targets


def test_all_local_links_resolve_to_existing_files():
    missing = []
    for name in PAGES:
        html = (DIST / name).read_text(encoding="utf-8")
        for target in _local_targets(html):
            if not (DIST / target).exists():
                missing.append(f"{name}: {target}")
    assert not missing, "kaputte lokale Links/Referenzen: " + ", ".join(missing)

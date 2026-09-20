from pathlib import Path

from html_utils import parse_elements

ROOT = Path(__file__).resolve().parent.parent
OG_PAGES = {
    "index.html": "https://thinkshark.de/",
    "projekt-izzy.html": "https://thinkshark.de/projekt-izzy.html",
    "projekt-bullseyeq.html": "https://thinkshark.de/projekt-bullseyeq.html",
    "projekt-bob.html": "https://thinkshark.de/projekt-bob.html",
    "projekt-desk-buddy.html": "https://thinkshark.de/projekt-desk-buddy.html",
}


def test_every_portfolio_page_carries_a_link_preview():
    for name, url in OG_PAGES.items():
        metas = [a for t, a in parse_elements((ROOT / name).read_text(encoding="utf-8")) if t == "meta"]
        prop = {a["property"]: a.get("content") for a in metas if a.get("property")}
        named = {a["name"]: a.get("content") for a in metas if a.get("name")}
        assert prop.get("og:url") == url, f"{name}: og:url"
        assert prop.get("og:type") == "website"
        assert prop.get("og:image") == "https://thinkshark.de/assets/og.jpg", f"{name}: og:image muss absolut sein"
        assert prop.get("og:title"), f"{name}: og:title fehlt"
        assert prop.get("og:description") == named.get("description"), f"{name}: og:description ≠ Meta-Description"
        assert named.get("twitter:card") == "summary_large_image"

from pathlib import Path

from html_utils import elements_by_tag

ROOT = Path(__file__).resolve().parent.parent
IMP = ROOT / "impressum.html"
DAT = ROOT / "datenschutz.html"
CHANGELOG = (ROOT / "changelog.html").read_text(encoding="utf-8")


def test_impressum_has_ddg_fields():
    html = IMP.read_text(encoding="utf-8")
    assert "Tjark Dreyer" in html
    assert "Reeseberg 178" in html
    assert "21079 Hamburg" in html
    assert "§ 5 DDG" in html
    assert "0171" not in html


def test_datenschutz_covers_logs_and_localstorage():
    html = DAT.read_text(encoding="utf-8")
    assert "Server-Log" in html
    assert "localStorage" in html
    assert "Kein Tracking" in html or "kein Tracking" in html


def test_legal_pages_are_german_only():
    for p in (IMP, DAT):
        html = p.read_text(encoding="utf-8")
        assert 'lang="de"' in html
        assert "data-en=" not in html


def test_all_pages_link_legal_pages():
    for name in [
        "index.html", "hub.html", "impressum.html", "datenschutz.html", "changelog.html",
        "projekt-izzy.html", "projekt-bullseyeq.html", "projekt-bob.html", "projekt-desk-buddy.html",
    ]:
        html = (ROOT / name).read_text(encoding="utf-8")
        hrefs = {a.get("href") for a in elements_by_tag(html, "a")}
        assert "impressum.html" in hrefs, f"{name}: kein <a href=\"impressum.html\">"
        assert "datenschutz.html" in hrefs, f"{name}: kein <a href=\"datenschutz.html\">"


def test_changelog_navigates_to_portfolio_and_hub():
    assert 'href="index.html"' in CHANGELOG
    assert 'href="hub.html"' in CHANGELOG


def test_changelog_loads_main_js_for_footer_year():
    assert 'id="year"' in CHANGELOG
    assert 'src="main.js"' in CHANGELOG

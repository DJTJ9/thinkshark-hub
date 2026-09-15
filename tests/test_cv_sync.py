"""Hält index.html und bewerbung/profil/master.md zusammen (Entscheidung 2026-09-15).

Der Kurzprofil-Absatz der Seite IST profil.de aus master.md, Wort für Wort — nur so
ist der Vergleich automatisierbar. Fehlt das Bewerbungs-Repo (anderer Rechner) oder
PyYAML, überspringt sich das Modul.
"""
import re
from pathlib import Path

import pytest

from html_utils import fragment, has_class, parse_elements, text_by_class

yaml = pytest.importorskip("yaml", reason="PyYAML nicht installiert — CV-Abgleich übersprungen")

ROOT = Path(__file__).resolve().parent.parent
MASTER = Path("/root/projekte/bewerbung/profil/master.md")

pytestmark = pytest.mark.skipif(
    not MASTER.exists(), reason=f"{MASTER} nicht vorhanden — CV-Abgleich übersprungen"
)

HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def _master():
    text = MASTER.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?", text, re.S)
    assert match, "kein YAML-Frontmatter in master.md"
    return yaml.safe_load(match.group(1))


def _norm(value):
    return " ".join((value or "").split())


def _about():
    return fragment(HTML, '<section id="ueber"', "</section>")


def test_short_profile_is_identical_in_both_places():
    data = _master()
    paras = [a for t, a in parse_elements(_about()) if t == "p"]
    page_de, page_en = _norm(paras[0].get("data-de")), _norm(paras[0].get("data-en"))
    assert page_de == _norm(data["profil"]["de"]), \
        "Kurzprofil (DE) weicht von profil.de in master.md ab"
    assert page_en == _norm(data["profil"]["en"]), \
        "Kurzprofil (EN) weicht von profil.en in master.md ab"


def test_role_is_identical_in_both_places():
    data = _master()
    roles = text_by_class(HTML, "p", "hero__role")
    assert roles, "keine .hero__role auf der Seite"
    assert _norm(roles[0]) == _norm(data["rolle"]["de"])


def test_skill_groups_and_chips_are_identical_in_both_places():
    data = _master()
    page = {}
    for chunk in re.split(r"<li>", fragment(HTML, '<ul class="skills"', "</ul>"))[1:]:
        label = [a for t, a in parse_elements(chunk) if t == "span" and has_class(a, "skills__group")][0]
        page[_norm(label["data-de"])] = text_by_class(chunk, "span", "chip")
    cv = {_norm(g["gruppe"]["de"]): list(g["chips"]) for g in data["skills"]}
    assert page == cv, "Skill-Gruppen oder Chips laufen zwischen Seite und CV auseinander"


def test_every_project_on_the_page_is_in_the_cv():
    data = _master()
    cv_titles = {_norm(p["titel"]) for p in data["projekte"]}
    page_titles = {_norm(t) for t in text_by_class(HTML, "h3", "project__title")}
    # Der WIP-Badge-Text hängt im selben <h3> — Titel auf das erste Wortstück reduzieren.
    page_titles = {t.split(" in Arbeit")[0].strip() for t in page_titles}
    missing = page_titles - cv_titles
    assert not missing, f"Projekte nur auf der Seite, nicht im CV: {sorted(missing)}"

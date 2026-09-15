import re
import shutil
import subprocess
from pathlib import Path

import pytest

from html_utils import elements_by_tag, jpeg_size

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "projects"
NAMES = ["izzy.png", "bullseyeq.png", "bob.png", "desk-buddy.png"]
PAGES = [
    "index.html", "hub.html", "impressum.html", "datenschutz.html", "changelog.html",
    "projekt-izzy.html", "projekt-bullseyeq.html", "projekt-bob.html", "projekt-desk-buddy.html",
]

# Erkennt telefonnummer-artige Ziffernfolgen (Ländervorwahl/Trennzeichen erlaubt),
# ohne auf eine konkrete Nummer zu prüfen.
PHONE_RUN_RE = re.compile(r"\+?\d[\d ./\-()]{5,}\d")
PHONE_DIGIT_MIN = 7


def test_all_project_images_exist():
    for n in NAMES:
        p = SHOTS / n
        assert p.exists(), f"fehlt: {n}"
        assert p.stat().st_size > 0


def test_images_are_png():
    for n in NAMES:
        assert (SHOTS / n).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cv_pdfs_exist():
    for n in ["cv-de.pdf", "cv-en.pdf"]:
        assert (ROOT / "assets" / "cv" / n).exists()


def test_images_are_16_by_10():
    for n in NAMES:
        data = (SHOTS / n).read_bytes()
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        assert width * 10 == height * 16, (
            f"{n} ist nicht 16:10: {width}x{height}"
        )


def test_favicon_is_local_svg_without_external_refs():
    favicon = ROOT / "favicon.svg"
    assert favicon.exists(), "favicon.svg fehlt"
    text = favicon.read_text(encoding="utf-8")
    assert text.strip().startswith("<svg") or "<svg" in text[:200]
    assert "<image" not in text, "favicon.svg bindet ein Rasterbild ein"
    # xmlns="http://www.w3.org/2000/svg" ist eine reine Namespace-Deklaration (kein Request);
    # ein echter externer Verweis würde als url(http...)/xlink:href/http(s) außerhalb des xmlns stehen.
    without_namespace_decl = text.replace('xmlns="http://www.w3.org/2000/svg"', "")
    assert "http://" not in without_namespace_decl and "https://" not in without_namespace_decl, \
        "favicon.svg referenziert eine externe URL"


def test_all_pages_link_favicon():
    for name in PAGES:
        html = (ROOT / name).read_text(encoding="utf-8")
        links = elements_by_tag(html, "link")
        icons = [l for l in links if l.get("rel") == "icon" and l.get("href") == "favicon.svg"]
        assert icons, f"{name} verlinkt favicon.svg nicht als icon"
        assert icons[0].get("type") == "image/svg+xml", f"{name}: favicon-Link ohne image/svg+xml"


def test_cv_pdfs_contain_no_phone_number():
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext nicht installiert")
    for n in ["cv-de.pdf", "cv-en.pdf"]:
        result = subprocess.run(
            ["pdftotext", "-raw", str(ROOT / "assets" / "cv" / n), "-"],
            capture_output=True, text=True, check=True,
        )
        text = result.stdout
        assert text.strip(), f"{n}: leere Textextraktion"
        for match in PHONE_RUN_RE.findall(text):
            digits = re.sub(r"\D", "", match)
            assert len(digits) < PHONE_DIGIT_MIN, (
                f"{n}: telefonnummer-artige Ziffernfolge gefunden: {match!r}"
            )


def test_portrait_placeholder_is_a_square_jpeg():
    p = ROOT / "assets" / "me.jpg"
    assert p.exists(), "assets/me.jpg fehlt"
    data = p.read_bytes()
    assert data[:3] == b"\xff\xd8\xff", "assets/me.jpg ist kein JPEG"
    width, height = jpeg_size(data)
    assert width == height, f"me.jpg ist nicht 1:1: {width}x{height}"


def test_readme_deploy_copies_every_page():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for page in sorted(p.name for p in ROOT.glob("*.html")):
        assert page in readme, f"{page} fehlt im Redeploy-cp in README.md"


def test_cv_pdfs_are_single_page_and_current():
    for n in ["cv-de.pdf", "cv-en.pdf"]:
        data = (ROOT / "assets" / "cv" / n).read_bytes()
        pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
        assert pages == 1, f"{n}: {pages} Seiten — der Web-CV bleibt einseitig"


def test_cv_pdfs_carry_the_new_profile():
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext nicht installiert")
    # Bindestrich-Umbrüche im PDF überleben den Whitespace-Join als "KI- Algorithmen",
    # deshalb wird jede Wortgrenze tolerant gesucht statt wörtlich.
    expected = {
        "cv-de.pdf": r"spielspezifischer\s*KI-\s*Algorithmen",
        "cv-en.pdf": r"game-\s*specific\s*AI\s*algorithms",
    }
    for n, pattern in expected.items():
        result = subprocess.run(
            ["pdftotext", "-raw", str(ROOT / "assets" / "cv" / n), "-"],
            capture_output=True, text=True, check=True,
        )
        text = " ".join(result.stdout.split())
        assert re.search(pattern, text), f"{n}: PDF trägt noch das alte Profil"
        assert re.search(r"Desk-\s*Buddy", text), f"{n}: Desk-Buddy fehlt im gerenderten CV"

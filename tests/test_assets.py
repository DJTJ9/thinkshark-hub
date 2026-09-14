import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "projects"
NAMES = ["izzy.png", "bullseyeq.png", "bob.png", "desk-buddy.png"]

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

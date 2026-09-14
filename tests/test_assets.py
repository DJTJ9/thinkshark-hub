from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "projects"
NAMES = ["izzy.png", "bullseyeq.png", "bob.png", "desk-buddy.png"]


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

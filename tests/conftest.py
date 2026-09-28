"""Baut dist/ einmal vor dem Testlauf, damit HTML-Tests nie gegen ein veraltetes dist/ laufen."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402

build.build(ROOT, ROOT / "dist")

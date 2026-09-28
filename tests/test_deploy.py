"""Auto-Deploy: push main → Action → ssh → scripts/deploy.sh (build, pytest, rsync)."""
import shutil
import subprocess

import pytest
from html_utils import ROOT

SCRIPT_PATH = ROOT / "scripts" / "deploy.sh"
SCRIPT = SCRIPT_PATH.read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")


def test_deploy_builds_and_tests_before_publishing():
    steps = ["git reset --hard origin/main", "python3 build.py", "python3 -m pytest tests/", "rsync -a --delete dist/"]
    positions = [SCRIPT.find(s) for s in steps]
    assert -1 not in positions, dict(zip(steps, positions))
    assert positions == sorted(positions), "Reihenfolge: reset, build, pytest, rsync"
    assert "set -euo pipefail" in SCRIPT


def test_deploy_script_is_parsed_before_it_runs():
    # git reset überschreibt das laufende Script; main() sorgt dafür, dass bash es vorher komplett liest
    assert SCRIPT.rstrip().endswith('main "$@"')
    assert "flock" in SCRIPT


@pytest.mark.skipif(not shutil.which("bash"), reason="bash nicht im PATH")
def test_deploy_script_is_valid_bash():
    res = subprocess.run(["bash", "-n", str(SCRIPT_PATH)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_workflow_deploys_on_push_to_main():
    assert "branches: [main]" in WORKFLOW
    for name in ("DEPLOY_SSH_KEY", "DEPLOY_HOST"):
        assert f"secrets.{name}" in WORKFLOW
    assert "StrictHostKeyChecking=accept-new" not in WORKFLOW and "StrictHostKeyChecking=no" not in WORKFLOW
    assert "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKot6MH5dxuWlKeAvknmiMvMJqIAwuMKrIQrEi3YECPo" in WORKFLOW

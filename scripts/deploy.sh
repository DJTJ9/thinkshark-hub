#!/usr/bin/env bash
# Auto-Deploy für thinkshark.de. Wird von der GitHub Action per ssh aufgerufen
# (authorized_keys: command="/opt/thinkshark-build/scripts/deploy.sh"). Rot = Live-Seite bleibt, wie sie ist.
set -euo pipefail

main() {
  local build_dir="${BUILD_DIR:-/opt/thinkshark-build}"
  local webroot="${WEBROOT:-/var/www/thinkshark-hub}"
  export PATH="/root/.nvm/versions/node/v24.16.0/bin:$PATH"

  exec 9>/tmp/thinkshark-deploy.lock
  flock 9

  cd "$build_dir"
  git fetch --quiet origin main
  git reset --hard origin/main
  python3 build.py
  python3 -m pytest tests/ -q
  rsync -a --delete dist/ "$webroot/"
  echo "deployed $(git rev-parse --short HEAD)"
}

main "$@"

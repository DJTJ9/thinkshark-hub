# ThinkShark Hub

Statische Landing-/Hub-Seite für `thinkshark.de` — Buttons zu den Subdomains, Basis fürs spätere Portfolio.

## Lokal ansehen
Beliebigen statischen Server im Repo-Root starten, z. B.:

    python3 -m http.server 8000

Dann `http://localhost:8000` öffnen.

## Deploy (Hetzner + Caddy)
Live unter https://thinkshark.de. DNS (`thinkshark.de` + `www`) zeigt auf den Hetzner-Server `195.201.121.96`, dort serviert Caddy die Seite als statischen file_server.

- Webroot: `/var/www/thinkshark-hub`
- Caddy-Block in `/etc/caddy/Caddyfile`: `thinkshark.de` (file_server) + `www.thinkshark.de` (301 → apex), TLS via Cloudflare-Origin-Cert.

**Redeploy nach Änderung** (kein Git-Auto-Deploy):

    cp index.html styles.css main.js /var/www/thinkshark-hub/

Caddy-Reload nur bei Config-Änderung nötig: `systemctl reload caddy`.

## Struktur
- `index.html` — Hero + Hub-Grid + Footer
- `styles.css` — „Abyssal/Sonar"-Design
- `main.js` — Sonar-Ping-Hover (respektiert reduced-motion)

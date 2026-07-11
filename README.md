# ThinkShark Hub

Statische Landing-/Hub-Seite für `thinkshark.de` — Buttons zu den Subdomains, Basis fürs spätere Portfolio.

## Lokal ansehen
Beliebigen statischen Server im Repo-Root starten, z. B.:

    python3 -m http.server 8000

Dann `http://localhost:8000` öffnen.

## Deploy (Cloudflare Pages)
1. Cloudflare Dashboard → Workers & Pages → Create → Pages → **Connect to Git** → dieses Repo (`DJTJ9/thinkshark-hub`), Branch `main`.
2. Build-Einstellungen: **Framework preset: None**, Build command: *(leer)*, Output directory: `/` (Root).
3. Nach dem ersten Deploy: **Custom domains** → `thinkshark.de` und `www.thinkshark.de` hinzufügen. Cloudflare aktualisiert die DNS-Records automatisch (ersetzt die bisherigen A-Records auf `89.31.143.90`).

## Struktur
- `index.html` — Hero + Hub-Grid + Footer
- `styles.css` — „Abyssal/Sonar"-Design
- `main.js` — Sonar-Ping-Hover (respektiert reduced-motion)

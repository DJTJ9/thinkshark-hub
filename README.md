# ThinkShark Hub

Statische Portfolio-Seite für `thinkshark.de` — Hero, About, vier Projekt-Cards, CV-Downloads und Kontakt, zweisprachig DE/EN. Die alten Hub-Buttons zu den Subdomains leben jetzt unter `hub.thinkshark.de`.

## Lokal ansehen
Beliebigen statischen Server im Repo-Root starten, z. B.:

    python3 -m http.server 8000

Dann `http://localhost:8000` öffnen.

## Deploy (Hetzner + Caddy)
Live unter https://thinkshark.de. DNS (`thinkshark.de` + `www` + `*.thinkshark.de`) zeigt auf den Hetzner-Server `195.201.121.96`, dort serviert Caddy die Seite als statischen file_server.

- Webroot: `/var/www/thinkshark-hub`
- Caddy-Block in `/etc/caddy/Caddyfile`:
  - `thinkshark.de` (file_server) — die Portfolio-Seite (`index.html`)
  - `www.thinkshark.de` (301 → apex)
  - `hub.thinkshark.de` (gleicher Webroot, `rewrite / /hub.html`) — die alten Tool-Cards. DNS und Cloudflare-Origin-Cert decken die Wildcard bereits ab, kein zusätzlicher DNS- oder Zertifikats-Schritt nötig.
  - TLS via Cloudflare-Origin-Cert.

**Redeploy nach Änderung** (kein Git-Auto-Deploy):

    cd /root/projekte/website
    cp index.html hub.html impressum.html datenschutz.html changelog.html \
       projekt-izzy.html projekt-bullseyeq.html projekt-bob.html projekt-desk-buddy.html \
       styles.css main.js changelog.js fonts.css patches.json /var/www/thinkshark-hub/
    cp fonts/*.woff2 /var/www/thinkshark-hub/fonts/
    cp -r assets /var/www/thinkshark-hub/

Caddy-Reload nur bei Config-Änderung nötig: `systemctl reload caddy`.

## Struktur
- `index.html` — Portfolio: Hero (Sonar-Ringe + Foto), „Wer ich bin" mit Aufklapper „Tiefer tauchen" (natives `<details>`, kein JS), fünf Skill-Gruppen mit dem Niveau im Label, vier Projekt-Cards mit „Mehr dazu", CV-Downloads, Kontakt; DE/EN via `data-de`/`data-en` + `localStorage`; Sprungnavigation: Depth-Rail ≥900px, sticky Kapitelleiste <900px
- **CV-Sync-Regel:** Kurzprofil, Rolle und die Skill-Gruppen stehen zusätzlich in `/root/projekte/bewerbung/profil/master.md`, aus dem `assets/cv/*.pdf` gerendert wird. Der Kurzprofil-Absatz IST `profil.de` (bzw. `data-en` = `profil.en`), Wort für Wort. `tests/test_cv_sync.py` macht jede Abweichung rot; ohne das Bewerbungs-Repo überspringt sich der Test. Wer eine der beiden Seiten ändert, ändert beide und rendert die PDFs neu (`render.py cv --lang de|en --web`).
- `projekt-izzy.html`, `projekt-bullseyeq.html`, `projekt-bob.html`, `projekt-desk-buddy.html` — Projekt-Detailseiten (Gerüst mit leeren Clip-Slots, Abschnitt „Meine Rolle")
- `hub.html` — die vier Tool-Cards, ehemals auf der Apex
- `impressum.html`, `datenschutz.html` — rechtliche Seiten, nur Deutsch
- `changelog.html`, `changelog.js`, `patches.json` — Changelog, unverändert im Inhalt
- `styles.css` — „Abyssal/Sonar"-Design, von allen Seiten geteilt
- `main.js` — DE/EN-Sprachumschalter mit localStorage, Depth-Rail-Marker, Mail-Deobfuskation, Footer-Jahr; Sonar-Ping-Hover nur auf hub.html (respektiert reduced-motion), null-safe, auf jeder Seite eingebunden
- `fonts.css`, `fonts/*.woff2` — Schriften, von allen Seiten geteilt
- `assets/projects/*.png` — Projektbilder (izzy, bullseyeq, bob, desk-buddy)
- `assets/cv/cv-de.pdf`, `assets/cv/cv-en.pdf` — öffentliche CV-Downloads (ohne Telefonnummer)
- `assets/me.jpg` — Porträt-Platzhalter im Hero (1:1), wird durch das echte Foto ersetzt
- `tests/` — Pytest-Suite (Markup, Inhalte, rechtliche Seiten, CSS-Scoping, Asset-Integrität)

## Tests
    python3 -m pytest tests/ -q

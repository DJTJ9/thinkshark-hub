# ThinkShark Hub

Statische Portfolio-Seite für `thinkshark.de` — Hero, About, vier Projekt-Cards, CV-Downloads und Kontakt, zweisprachig DE/EN. Die alten Hub-Buttons zu den Subdomains leben jetzt unter `hub.thinkshark.de`.

## Lokal ansehen
    python build.py
    python -m http.server 8000 -d dist

Dann `http://localhost:8000` öffnen. (Server: `python3`.)

## Texte bearbeiten
Die Texte der fünf zweisprachigen Seiten stehen in `content/<seite>.de.md` und `content/<seite>.en.md`, nicht im HTML. Jeder Block beginnt mit `## schlüssel`, darunter der Text (Plain Text, Zeilenumbrüche werden zu Leerzeichen). Titel und Beschreibung der Seite stehen im Front-Matter der `.de.md`. Die Vorlagen in `templates/` tragen nur die Schlüssel (`data-t`, `data-t-alt`, `data-t-href`). `build.py` bricht hart ab, wenn ein Schlüssel in einer Sprache fehlt, doppelt oder verwaist ist.
Neuer Text: Element mit `data-t="seite.abschnitt.n"` in die Vorlage, Block mit demselben Schlüssel in beide `.md`-Dateien.

## Deploy (Hetzner + Caddy)
Live unter https://thinkshark.de. DNS (`thinkshark.de` + `www` + `*.thinkshark.de`) zeigt auf den Hetzner-Server `195.201.121.96`, dort serviert Caddy die Seite als statischen file_server.

- Webroot: `/var/www/thinkshark-hub`
- Caddy-Block in `/etc/caddy/Caddyfile`:
  - `thinkshark.de` (file_server) — die Portfolio-Seite (`index.html`)
  - `www.thinkshark.de` (301 → apex)
  - `hub.thinkshark.de` (gleicher Webroot, `rewrite / /hub.html`) — die alten Tool-Cards. DNS und Cloudflare-Origin-Cert decken die Wildcard bereits ab, kein zusätzlicher DNS- oder Zertifikats-Schritt nötig.
  - TLS via Cloudflare-Origin-Cert.

**Deploy = `git push` auf `main`.** Die GitHub Action `deploy` ruft per ssh `scripts/deploy.sh` auf dem Server auf. Das Script setzt den Build-Clone `/opt/thinkshark-build` auf `origin/main`, baut `dist/`, lässt die Tests laufen und spiegelt `dist/` bei Grün per `rsync --delete` nach `/var/www/thinkshark-hub`. Rote Tests = Action rot, die Live-Seite bleibt unverändert. Der Deploy-Key ist in `authorized_keys` per `command=` auf genau dieses Script beschränkt. Status und Logs: Actions-Tab im Repo.

Caddy-Reload nur bei Config-Änderung nötig: `systemctl reload caddy`.

## Struktur
- `build.py` — füllt die Schlüssel der Vorlagen aus `content/` und kopiert die statischen Dateien (Whitelist `STATIC`) nach `dist/` (nicht im Git)
- `content/*.de.md`, `content/*.en.md` — alle Texte der fünf zweisprachigen Seiten
- `scripts/deploy.sh`, `.github/workflows/deploy.yml` — Auto-Deploy bei Push auf `main`
- `templates/index.html` — Portfolio: Hero (Sonar-Ringe + Foto), „Über mich" mit immer sichtbarem Block „Was mich antreibt", zwei Hero-CTAs (Projekte / CV in Seitensprache), Rail mit Gruppenmarker „Projekte", fünf Skill-Gruppen mit dem Niveau im Label, vier Projekt-Cards mit „Mehr dazu", CV-Downloads, Kontakt; DE/EN via `data-de`/`data-en` + `localStorage`; Sprungnavigation: Depth-Rail ≥900px, sticky Kapitelleiste <900px
- **CV-Sync-Regel:** Kurzprofil, Rolle und die Skill-Gruppen stehen zusätzlich in `/root/projekte/bewerbung/profil/master.md`, aus dem `assets/cv/*.pdf` gerendert wird. Der Kurzprofil-Absatz IST `profil.de` (bzw. `data-en` = `profil.en`), Wort für Wort. Er steht in `content/index.de.md` bzw. `content/index.en.md`. `tests/test_cv_sync.py` macht jede Abweichung rot; ohne das Bewerbungs-Repo überspringt sich der Test. Wer eine der beiden Seiten ändert, ändert beide und rendert die PDFs neu (`render.py cv --lang de|en --web`).
- `templates/projekt-*.html` — Projekt-Detailseiten (Rolle in „Worum es geht", Fußnavigation „Nächstes Projekt"/„Kontakt"; nur Izzy trägt Clips — ein offener Block pro Minispiel)
- `hub.html` — die vier Tool-Cards, ehemals auf der Apex
- `impressum.html`, `datenschutz.html` — rechtliche Seiten, nur Deutsch
- `changelog.html`, `changelog.js`, `patches.json` — Changelog, unverändert im Inhalt
- `styles.css` — „Abyssal/Sonar"-Design, von allen Seiten geteilt
- `main.js` — DE/EN-Sprachumschalter mit localStorage, Depth-Rail-Marker, Scrolltiefe als `--depth` (0..1, nur `.portfolio`), Mail-Deobfuskation, Footer-Jahr; Sonar-Ping-Hover nur auf hub.html (respektiert reduced-motion), null-safe, auf jeder Seite eingebunden
- `sea.js` — „Lebendiges Meer": Boids-Schwarm + Hai + Partikel auf einem fixen Canvas (erzeugt es selbst), liest `--depth` und den Pointer; reiner Simulationskern per node getestet (`tests/test_sea.py`); Detailseiten nur Partikel; reduced-motion = Standbild
- `fonts.css`, `fonts/*.woff2` — Schriften, von allen Seiten geteilt
- `assets/projects/` — Projektbilder: `izzy.png`, `bob.png`, `desk-buddy.png`, `bullseyeq.webp` (Karte 800×500) und `bullseyeq-*.webp` (Detail-Shots 1280×720, aus der DartApp im Play Mode mit Demo-Daten)
- `assets/cv/cv-de.pdf`, `assets/cv/cv-en.pdf` — öffentliche CV-Downloads (ohne Telefonnummer)
- `assets/clips/{minigolf,swaggy,bowling}.{mp4,jpg}` — drei Izzy-Loops (720p30, H.264, ohne Ton, < 10 MB) plus Poster; das Rohmaterial bleibt in `/root/uploads/portfolio-videos/` und gehört nicht ins Git
- `assets/og.jpg` — Link-Vorschau (1200×630), von allen Portfolio-Seiten per `og:image` referenziert; gerendert aus dem Hero mit `python3 scripts/make_og.py` (Playwright, braucht einen lokalen Server)
- `assets/me.jpg` — Porträt im Hero (1:1, 440×440, rund maskiert). Wird die Datei getauscht, muss `assets/og.jpg` neu gerendert werden, sonst zeigt die Link-Vorschau das alte Bild
- `scripts/verify_portfolio.py` — gerenderte Verifikation per Playwright (Default LIVE; lokal mit `PORTFOLIO_BASE`/`PORTFOLIO_HUB`), Screenshots in `/tmp/portfolio-verify/` — ansehen, nicht nur den Exit-Code lesen
- `tests/` — Pytest-Suite (Markup, Inhalte, rechtliche Seiten, CSS-Scoping, Asset-Integrität)

## Tests
    python3 -m pytest tests/ -q

Der Testlauf baut `dist/` vorher selbst (`tests/conftest.py`).

`tests/test_sea.py` braucht `node`, die Clip-Prüfungen in `tests/test_assets.py` brauchen `ffprobe` — beide überspringen sich, wenn das Werkzeug nicht im `PATH` liegt (auf dem Server: `PATH=/root/.nvm/versions/node/v24.16.0/bin:$PATH`).

"""Baut dist/ aus templates/ und content/ (nur Standardbibliothek).

templates/<seite>.html  HTML mit data-t / data-t-alt / data-t-href Schlüsseln
content/<seite>.de.md   Front-Matter (title, description) + "## schlüssel"-Blöcke
content/<seite>.en.md   nur "## schlüssel"-Blöcke

Aufruf: python3 build.py   (exit 1 mit Meldung bei jedem Content-Fehler)
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATIC = (
    "impressum.html", "datenschutz.html", "hub.html", "changelog.html",
    "styles.css", "main.js", "sea.js", "changelog.js", "fonts.css",
    "patches.json", "favicon.svg", "fonts", "assets",
)
LANGS = ("de", "en")
META_KEYS = ("title", "description")
META_TAGS = (("name", "description", "description"),
             ("property", "og:title", "title"),
             ("property", "og:description", "description"))

_START_TAG = re.compile(r'<([a-zA-Z][\w-]*)((?:[^>"]|"[^"]*")*)>')
_MARKER = re.compile(r'\sdata-t(-alt|-href)?="([^"]*)"')
_LEFTOVER = re.compile(r'\sdata-t(?:-alt|-href)?="([^"]*)"')


class BuildError(Exception):
    pass


def _attr(value):
    return html.escape(value, quote=True)


def parse_content(path):
    """-> (meta, blocks): Front-Matter als dict, Blöcke als {schlüssel: text} in Dateireihenfolge."""
    lines = path.read_text(encoding="utf-8").splitlines()
    meta = {}
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            raise BuildError(f"{path.name}: Front-Matter ohne schließendes ---")
        for line in lines[1:end]:
            if not line.strip():
                continue
            key, sep, value = line.partition(":")
            if not sep:
                raise BuildError(f"{path.name}: Front-Matter-Zeile ohne ':': {line.strip()}")
            meta[key.strip()] = value.strip()
        lines = lines[end + 1:]

    blocks, key, buf = {}, None, []

    def flush():
        if key is None:
            return
        text = " ".join(line.strip() for line in buf if line.strip())
        if not text:
            raise BuildError(f"{path.name}: Schlüssel '{key}' ohne Text")
        blocks[key] = text

    for line in lines:
        if line.startswith("## "):
            flush()
            key, buf = line[3:].strip(), []
            if key in blocks:
                raise BuildError(f"{path.name}: Schlüssel '{key}' doppelt")
        elif key is None:
            if line.strip():
                raise BuildError(f"{path.name}: Text vor dem ersten '## schlüssel': {line.strip()[:60]}")
        else:
            buf.append(line)
    flush()
    return meta, blocks


def fill_page(template, name, texts, meta):
    """Ersetzt alle Schlüssel einer Vorlage. texts = {"de": {...}, "en": {...}}."""
    stem = Path(name).stem
    used = set()

    def lookup(key):
        missing = [f"{stem}.{lang}.md" for lang in LANGS if key not in texts[lang]]
        if missing:
            raise BuildError(f"{name}: Schlüssel '{key}' fehlt in {', '.join(missing)}")
        used.add(key)
        return texts["de"][key], texts["en"][key]

    out, pos = [], 0
    for m in _START_TAG.finditer(template):
        if "data-t" not in m.group(2):
            continue
        tag, content_key = m.group(1), None

        def repl(a):
            nonlocal content_key
            kind, key = a.group(1), a.group(2)
            de, en = lookup(key)
            if kind is None:
                content_key = key
                return f' data-de="{_attr(de)}" data-en="{_attr(en)}"'
            base = kind[1:]
            return f' {base}="{_attr(de)}" data-{base}-de="{_attr(de)}" data-{base}-en="{_attr(en)}"'

        attrs = _MARKER.sub(repl, m.group(2))
        out.append(template[pos:m.start()])
        out.append(f"<{tag}{attrs}>")
        pos = m.end()
        if content_key:
            close = re.compile(rf"</{tag}\s*>").search(template, pos)
            if close is None or "<" in template[pos:close.start()]:
                raise BuildError(f'{name}: Element mit data-t="{content_key}" darf nur Text enthalten')
            out.append(html.escape(texts["de"][content_key], quote=False))
            pos = close.start()
    out.append(template[pos:])
    page = "".join(out)

    leftover = _LEFTOVER.search(page)
    if leftover:
        raise BuildError(f'{name}: Schlüssel "{leftover.group(1)}" nicht ersetzt (Tag nicht erkannt)')
    for lang in LANGS:
        orphans = sorted(set(texts[lang]) - used)
        if orphans:
            raise BuildError(f"{name}: verwaiste Schlüssel in {stem}.{lang}.md: {', '.join(orphans)}")
    return _fill_meta(page, name, meta)


def _fill_meta(page, name, meta):
    stem = Path(name).stem
    for key in meta:
        if key not in META_KEYS:
            raise BuildError(f"{stem}.de.md: unbekanntes Front-Matter-Feld '{key}'")
    for key in META_KEYS:
        if not meta.get(key):
            raise BuildError(f"{name}: Front-Matter '{key}' fehlt in {stem}.de.md")
    page, n = re.subn(r"<title></title>", lambda _: f"<title>{html.escape(meta['title'], quote=False)}</title>", page)
    if n != 1:
        raise BuildError(f"{name}: Vorlage ohne leeres <title></title>")
    for attr_name, attr_value, key in META_TAGS:
        tag = f'<meta {attr_name}="{attr_value}" content="'
        page, n = re.subn(re.escape(tag) + '"', lambda _: tag + _attr(meta[key]) + '"', page)
        if n != 1:
            raise BuildError(f'{name}: Vorlage ohne <meta {attr_name}="{attr_value}" content="">')
    return page


def build(root=ROOT, out=None, static=STATIC):
    """Prüft alles, dann schreibt dist/ neu. Bei Fehler bleibt ein altes dist/ unangetastet."""
    root = Path(root)
    out = Path(out) if out else root / "dist"
    templates = sorted((root / "templates").glob("*.html"))
    if not templates:
        raise BuildError("templates/ enthält keine Seiten")
    stems = {t.stem for t in templates}
    for md in sorted((root / "content").glob("*.md")):
        if md.name.split(".")[0] not in stems:
            raise BuildError(f"content/{md.name} ohne Vorlage in templates/")

    pages = {}
    for tpl in templates:
        texts, meta = {}, {}
        for lang in LANGS:
            path = root / "content" / f"{tpl.stem}.{lang}.md"
            if not path.exists():
                raise BuildError(f"{tpl.name}: content/{path.name} fehlt")
            file_meta, texts[lang] = parse_content(path)
            if lang == "de":
                meta = file_meta
            elif file_meta:
                raise BuildError(f"{path.name}: Front-Matter nur in {tpl.stem}.de.md")
        pages[tpl.name] = fill_page(tpl.read_text(encoding="utf-8"), tpl.name, texts, meta)
    for item in static:
        if not (root / item).exists():
            raise BuildError(f"statische Datei fehlt: {item}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name, text in pages.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
    for item in static:
        src = root / item
        if src.is_dir():
            shutil.copytree(src, out / item)
        else:
            shutil.copy2(src, out / item)
    return sorted(pages)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        pages = build()
    except BuildError as e:
        print(f"build.py: {e}", file=sys.stderr)
        return 1
    print(f"dist/: {len(pages)} Seiten gebaut")
    return 0


if __name__ == "__main__":
    sys.exit(main())

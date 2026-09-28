"""Einmalige Migration (wird nach der Abnahme gelöscht).

python scripts/extract_content.py           schreibt templates/ + content/ aus den 5 Root-Seiten
python scripts/extract_content.py --verify  vergleicht dist/ DOM-genau mit den 9 Root-Seiten
"""
import argparse
import html
import re
import sys
import textwrap
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "index.html": "home",
    "projekt-izzy.html": "izzy",
    "projekt-bullseyeq.html": "bullseyeq",
    "projekt-bob.html": "bob",
    "projekt-desk-buddy.html": "desk-buddy",
}
ALL_PAGES = list(PAGES) + ["hub.html", "impressum.html", "datenschutz.html", "changelog.html"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
META = {("name", "description"): "description",
        ("property", "og:title"): "title",
        ("property", "og:description"): "description"}


class _Scanner(HTMLParser):
    """Start-Tags mit Offset, Attributen und Abschnittsnamen (aus den Vorfahren)."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self._line_starts = [0] + [m.end() for m in re.finditer("\n", text)]
        self.stack, self.tags, self._articles = [], [], 0

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        start = self._line_starts[line - 1] + col
        a = dict(attrs)
        self.tags.append({"tag": tag, "attrs": a, "start": start,
                          "end": start + len(self.get_starttag_text()), "section": self._section()})
        if tag == "article":
            self._articles += 1
        if tag not in VOID:
            self.stack.append((tag, a, self._articles))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def _section(self):
        for tag, a, n in reversed(self.stack):
            if a.get("id"):
                return a["id"]
            if tag == "article":
                return f"{(a.get('class') or 'article').split()[0]}{n}"
            if tag in ("nav", "header", "footer"):
                return (a.get("class") or tag).split()[0].replace("__", "-")
            if tag == "main":
                return "main"
        return "page"


def _drop(tag_text, name):
    return re.sub(rf'\s+{re.escape(name)}="[^"]*"', "", tag_text, count=1)


def _swap(tag_text, name, replacement):
    new, n = re.subn(rf'(\s){re.escape(name)}="[^"]*"', lambda m: m.group(1) + replacement, tag_text, count=1)
    if n != 1:
        raise SystemExit(f"Attribut {name} nicht gefunden in {tag_text[:80]}")
    return new


def _norm(text):
    return " ".join(text.split())


def extract(text, prefix):
    """-> (vorlage, meta, de, en). Vorlage trägt nur noch Schlüssel."""
    sc = _Scanner(text)
    sc.feed(text)
    sc.close()
    edits, de, en, meta, counters = [], {}, {}, {}, {}

    def remember(field, value):
        value = _norm(value)
        if meta.setdefault(field, value) != value:
            raise SystemExit(f"{prefix}: {field} weicht ab: {meta[field]!r} != {value!r}")

    title = re.search(r"<title>(.*?)</title>", text, re.S)
    remember("title", html.unescape(title.group(1)))
    edits.append((title.start(), title.end(), "<title></title>"))

    for t in sc.tags:
        a, raw = t["attrs"], text[t["start"]:t["end"]]
        if t["tag"] == "meta":
            field = META.get(("name", a.get("name"))) or META.get(("property", a.get("property")))
            if field:
                remember(field, a["content"])
                edits.append((t["start"], t["end"], re.sub(r'content="[^"]*"', 'content=""', raw)))
            continue
        if not any(k in a for k in ("data-de", "data-alt-de", "data-href-de")):
            continue
        counters[t["section"]] = counters.get(t["section"], 0) + 1
        base = f"{prefix}.{t['section']}.{counters[t['section']]}"
        new = raw
        if "data-de" in a:
            close = text.index(f"</{t['tag']}>", t["end"])
            inner = text[t["end"]:close]
            if "<" in inner or _norm(html.unescape(inner)) != _norm(a["data-de"]):
                raise SystemExit(f"{base}: Inhalt ist nicht der DE-Text: {inner[:80]!r}")
            de[base], en[base] = _norm(a["data-de"]), _norm(a["data-en"])
            new = _swap(_drop(new, "data-en"), "data-de", f'data-t="{base}"')
            edits.append((t["end"], close, ""))
        for kind in ("alt", "href"):
            if f"data-{kind}-de" in a:
                key = f"{base}.{kind}"
                if a.get(kind) != a[f"data-{kind}-de"]:
                    raise SystemExit(f"{key}: {kind} weicht von data-{kind}-de ab")
                de[key], en[key] = _norm(a[f"data-{kind}-de"]), _norm(a[f"data-{kind}-en"])
                new = _drop(_drop(new, f"data-{kind}-de"), f"data-{kind}-en")
                new = _swap(new, kind, f'data-t-{kind}="{key}"')
        edits.append((t["start"], t["end"], new))

    for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
        text = text[:start] + replacement + text[end:]
    return text, meta, de, en


def to_markdown(blocks, meta=None):
    parts = []
    if meta:
        parts.append("---\n" + "".join(f"{k}: {meta[k]}\n" for k in ("title", "description")) + "---\n")
    for key, text in blocks.items():
        body = textwrap.fill(text, width=100, break_long_words=False, break_on_hyphens=False)
        parts.append(f"## {key}\n{body}\n")
    return "\n".join(parts)


class _Dom(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []

    def handle_starttag(self, tag, attrs):
        self.events.append(("start", tag, tuple(sorted((k, _norm(v or "")) for k, v in attrs))))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))

    def handle_data(self, data):
        if data.strip():
            self.events.append(("text", _norm(data)))


def dom(text):
    parser = _Dom()
    parser.feed(text)
    parser.close()
    return parser.events


def verify(baseline_dir, dist_dir, pages=ALL_PAGES):
    diffs = []
    for name in pages:
        a = dom((Path(baseline_dir) / name).read_text(encoding="utf-8"))
        b = dom((Path(dist_dir) / name).read_text(encoding="utf-8"))
        if a == b:
            continue
        i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        diffs.append(f"{name}: Ereignis {i}: {a[i] if i < len(a) else 'ENDE'} != {b[i] if i < len(b) else 'ENDE'}")
    return diffs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        diffs = verify(ROOT, ROOT / "dist")
        print("\n".join(diffs) if diffs else f"DOM-gleich: {len(ALL_PAGES)} Seiten")
        return 1 if diffs else 0
    (ROOT / "templates").mkdir(exist_ok=True)
    (ROOT / "content").mkdir(exist_ok=True)
    total = 0
    for name, prefix in PAGES.items():
        tpl, meta, de, en = extract((ROOT / name).read_text(encoding="utf-8"), prefix)
        stem = Path(name).stem
        (ROOT / "templates" / name).write_text(tpl, encoding="utf-8", newline="\n")
        (ROOT / "content" / f"{stem}.de.md").write_text(to_markdown(de, meta), encoding="utf-8", newline="\n")
        (ROOT / "content" / f"{stem}.en.md").write_text(to_markdown(en), encoding="utf-8", newline="\n")
        total += len(de)
        print(f"{name}: {len(de)} Schlüssel")
    print(f"gesamt: {total} Schlüssel")
    return 0


if __name__ == "__main__":
    sys.exit(main())

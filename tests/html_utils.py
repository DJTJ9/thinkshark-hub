"""Kleine, dependency-freie Helfer zum Parsen von HTML/CSS in Tests.

Nutzt nur die Python-Stdlib (html.parser), damit das No-Dependencies-Prinzip
des Repos erhalten bleibt.
"""
import re
from html.parser import HTMLParser

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


class _ElementCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []  # list of (tag, attrs_dict)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def parse_elements(html_text):
    """Gibt eine Liste von (tagname, attrs-dict) in Dokumentreihenfolge zurück."""
    parser = _ElementCollector()
    parser.feed(html_text)
    return parser.elements


def elements_by_tag(html_text, tag):
    return [attrs for t, attrs in parse_elements(html_text) if t == tag]


def has_class(attrs, cls):
    return cls in (attrs.get("class") or "").split()


def parse_css_rules(css_text):
    """Sehr einfacher CSS-Parser: liefert eine flache Liste von Regeln.

    Jede Regel ist {"selectors": [...], "body": "...", "media": str|None}.
    @media/@supports-Blöcke werden als Container behandelt (ein Nesting-Level,
    ausreichend für dieses Stylesheet); alles andere mit einem Body wird als
    Blattregel behandelt.
    """
    css_text = _COMMENT_RE.sub("", css_text)
    rules = []
    stack = []
    i = 0
    n = len(css_text)
    while i < n:
        open_idx = css_text.find("{", i)
        close_idx = css_text.find("}", i)
        if open_idx == -1 and close_idx == -1:
            break
        if close_idx != -1 and (open_idx == -1 or close_idx < open_idx):
            if stack:
                stack.pop()
            i = close_idx + 1
            continue
        prelude = css_text[i:open_idx].strip()
        if prelude.startswith("@"):
            stack.append(prelude)
            i = open_idx + 1
            continue
        close2 = css_text.find("}", open_idx)
        if close2 == -1:
            break
        body = css_text[open_idx + 1:close2]
        selectors = [s.strip() for s in prelude.split(",") if s.strip()]
        rules.append({"selectors": selectors, "body": body, "media": stack[-1] if stack else None})
        i = close2 + 1
    return rules


def rules_for_selector(css_text, selector, media=None):
    """Regeln, deren Selektorliste `selector` exakt enthält (nicht Substring)."""
    out = []
    for rule in parse_css_rules(css_text):
        if selector in rule["selectors"]:
            if media is None or (rule["media"] and media in rule["media"]):
                out.append(rule)
    return out


def fragment(html_text, start_marker, end_marker):
    """Teilstring vom ersten `start_marker` bis zum nächsten `end_marker`.

    Nur zum Eingrenzen des Bereichs; die eigentlichen Assertions laufen
    danach über parse_elements() auf diesem Ausschnitt.
    """
    start = html_text.index(start_marker)
    end = html_text.index(end_marker, start)
    return html_text[start:end + len(end_marker)]


def element_ids(html_text):
    return {attrs["id"] for _, attrs in parse_elements(html_text) if attrs.get("id")}


def jpeg_size(data):
    """(width, height) aus dem SOF-Marker einer JPEG-Datei — stdlib only."""
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height = int.from_bytes(data[i + 5:i + 7], "big")
            width = int.from_bytes(data[i + 7:i + 9], "big")
            return width, height
        i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    raise ValueError("kein SOF-Marker gefunden")


class _TextCollector(HTMLParser):
    """Sammelt den Textinhalt aller <tag class="cls">-Elemente (ohne Verschachtelung derselben Klasse)."""

    def __init__(self, tag, cls):
        super().__init__(convert_charrefs=True)
        self.tag, self.cls = tag, cls
        self.out, self._depth, self._buf = [], 0, []

    def handle_starttag(self, tag, attrs):
        if self._depth:
            if tag == self.tag:
                self._depth += 1
            return
        if tag == self.tag and has_class(dict(attrs), self.cls):
            self._depth, self._buf = 1, []

    def handle_data(self, data):
        if self._depth:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._depth and tag == self.tag:
            self._depth -= 1
            if self._depth == 0:
                self.out.append("".join(self._buf).strip())


def text_by_class(html_text, tag, cls):
    """Textinhalte aller <tag class="cls"> in Dokumentreihenfolge."""
    parser = _TextCollector(tag, cls)
    parser.feed(html_text)
    return parser.out

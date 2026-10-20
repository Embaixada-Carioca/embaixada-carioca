#!/usr/bin/env python3
"""Gera a versão em Markdown de cada página do sitemap, para agentes de IA.

Usado por build_cloudflare_pages.py: grava _site/_md/<caminho>.md, que a
Function (functions/[[path]].js) serve em /<caminho>.md e quando o pedido traz
"Accept: text/markdown". Só usa a biblioteca padrão.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.embaixadacarioca.com"
SKIP_TAGS = {"script", "style", "noscript", "svg", "form", "button", "iframe", "template", "picture", "img", "source"}
SKIP_CLASSES = ("visit-breadcrumbs", "ec-growth-links", "mobile-actions", "skip-link", "visually-hidden", "sr-only", "visit-hero-actions")
BLOCK = {"p", "div", "section", "article", "header", "footer", "main", "aside", "figure", "figcaption", "ul", "ol", "table", "details", "summary", "dl", "address", "nav"}


class MainToMarkdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0
        self.stack: list[str] = []
        self.lists: list[list] = []  # [tag, counter]
        self.link: str | None = None
        self.link_text: list[str] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.table: list[list[str]] | None = None
        self.heading: str | None = None

    def emit(self, text: str) -> None:
        if self.cell is not None:
            self.cell.append(text)
        elif self.link is not None:
            self.link_text.append(text)
        else:
            self.out.append(text)

    def handle_starttag(self, tag, attrs):
        if tag not in ("span", "dd"):
            self.after_strong = False
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.skip or tag in SKIP_TAGS or any(c in cls.split() for c in SKIP_CLASSES) or a.get("aria-hidden") == "true" or "hidden" in a:
            if tag not in ("img", "source", "br", "input", "meta", "link"):
                self.skip += 1
            return
        self.stack.append(tag)
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
            self.heading = tag
        elif tag in ("ul", "ol"):
            self.lists.append([tag, 0])
            self.out.append("\n")
        elif tag == "li":
            depth = max(len(self.lists) - 1, 0)
            if self.lists and self.lists[-1][0] == "ol":
                self.lists[-1][1] += 1
                self.emit("\n" + "  " * depth + f"{self.lists[-1][1]}. ")
            else:
                self.emit("\n" + "  " * depth + "- ")
        elif tag == "br":
            self.emit("  \n")
        elif tag in ("strong", "b"):
            self.emit("**")
        elif tag == "a" and a.get("href") and self.cell is None:
            href = a["href"]
            if href.startswith("/"):
                href = SITE + href
            self.link, self.link_text = href, []
        elif tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = []
        elif tag == "summary":
            self.out.append("\n\n### ")
        elif tag in BLOCK:
            self.out.append("\n\n")

    def handle_endtag(self, tag):
        if self.skip:
            if tag not in ("img", "source", "br", "input", "meta", "link"):
                self.skip -= 1
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag in ("h1", "h2", "h3", "h4"):
            self.heading = None
            self.out.append("\n")
        elif tag in ("ul", "ol"):
            if self.lists:
                self.lists.pop()
            self.out.append("\n")
        elif tag in ("strong", "b"):
            self.emit("**")
            self.after_strong = True
            return
        elif tag == "a" and self.link is not None:
            text = re.sub(r"\s+", " ", "".join(self.link_text)).strip()
            href, self.link = self.link, None
            if text:
                self.emit(f"[{text}]({href}) ")
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip().replace("|", "\\|"))
            self.cell = None
        elif tag == "tr" and self.row is not None and self.table is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            rows, self.table = self.table, None
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [""] * (width - len(r)) for r in rows]
                lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                self.out.append("\n\n" + "\n".join(lines) + "\n\n")
        elif tag == "summary":
            self.out.append("\n\n")
        elif tag in BLOCK:
            self.out.append("\n\n")

    def handle_data(self, data):
        if self.skip:
            return
        text = re.sub(r"\s+", " ", data)
        if getattr(self, "after_strong", False) and text.strip() and self.stack and self.stack[-1] in ("span", "dd"):
            text = ": " + text.lstrip()
        self.after_strong = False
        if text.strip() or (text and self.out and not self.out[-1].endswith((" ", "\n"))):
            self.emit(text)

    def markdown(self) -> str:
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n[ \t]+(?=[^-\d\s])", "\n", text)
        text = re.sub(r"\*\*\s*\*\*", "", text)
        text = re.sub(r"\) ([.,;:!?])", r")\1", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def page_markdown(page_html: str, url: str) -> str:
    title = html.unescape(re.search(r"<title>(.*?)</title>", page_html, re.S).group(1).strip())
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', page_html)
    desc = html.unescape(desc_m.group(1)) if desc_m else ""
    start, end = page_html.find("<main"), page_html.find("</main>")
    parser = MainToMarkdown()
    parser.feed(page_html[start:end])
    body = parser.markdown()
    modified = re.search(r'"dateModified":\s*"([^"]+)"', page_html)
    lang = "en" if "/en/" in url else "es" if "/es/" in url else "pt"
    lab = {"pt": {"source": "Fonte", "updated": "Atualizado em"}, "en": {"source": "Source", "updated": "Updated"},
           "es": {"source": "Fuente", "updated": "Actualizado el"}}[lang]
    lines = body.split("\n")
    h1_index = next((i for i, line in enumerate(lines) if line.startswith("# ")), None)
    h1 = lines.pop(h1_index) if h1_index is not None else f"# {title}"
    intro = [h1, "", f"> {desc}" if desc else "", "",
             f"{lab['source']}: {url}" + (f" · {lab['updated']} {modified.group(1)}" if modified else ""), ""]
    body = "\n".join(lines)
    footer = ["", "---", "", "Embaixada Carioca · Morro da Urca, Parque Bondinho Pão de Açúcar · Av. Pasteur, 520, Urca, Rio de Janeiro · +55 21 96683-7556"]
    return "\n".join(intro) + body.strip() + "\n" + "\n".join(footer) + "\n"


def markdown_path(path: str) -> str:
    return path + "index.md" if path.endswith("/") else re.sub(r"\.html$", ".md", path)


def sitemap_paths() -> list[str]:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return [u.replace(SITE, "") for u in re.findall(r"<loc>([^<]+)</loc>", text)]


def source_file(path: str) -> Path:
    if path.endswith("/"):
        return ROOT / (path.lstrip("/") + "index.html")
    return ROOT / path.lstrip("/")


def write_all(output: Path) -> int:
    count = 0
    for path in sitemap_paths():
        src = source_file(path)
        if not src.exists():
            continue
        md = page_markdown(src.read_text(encoding="utf-8"), SITE + path)
        target = output / "_md" / markdown_path(path).lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(md, encoding="utf-8")
        count += 1
    return count


if __name__ == "__main__":
    import sys
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    print(f"{write_all(out)} páginas em Markdown em {out / '_md'}")

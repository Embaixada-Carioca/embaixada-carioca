#!/usr/bin/env python3
"""Marca a data de atualização das páginas (visível, JSON-LD e sitemap).

Uso:
  python3 scripts/stamp_page_dates.py --date 2026-10-20            # todas as páginas do sitemap
  python3 scripts/stamp_page_dates.py --date 2026-10-20 almoco.html en/almoco.html
  python3 scripts/stamp_page_dates.py --check                      # só confere, não altera

Para cada página:
- mostra "Atualizado em <data>" (PT), "Updated on <date>" (EN) ou "Actualizado el <fecha>" (ES)
  no fim do conteúdo principal, num <time datetime>;
- grava "dateModified" no nó WebPage/Article do JSON-LD (cria um nó WebPage se não houver);
- atualiza <lastmod> da URL no sitemap.xml.
Rodar de novo só troca a data: o script é idempotente.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.embaixadacarioca.com"
PAGE_TYPES = {"WebPage", "AboutPage", "ContactPage", "FAQPage", "CollectionPage", "ItemPage", "Article", "BlogPosting", "NewsArticle", "MenuPage"}
MONTHS = {
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}
LANG_CODE = {"pt": "pt-BR", "en": "en", "es": "es"}
STAMP_RE = re.compile(r'<p class="ec-updated"[^>]*>[\s\S]*?</p>')
JSONLD_RE = re.compile(r'(<script[^>]+application/ld\+json[^>]*>)([\s\S]*?)(</script>)')


def lang_of(rel: str) -> str:
    return rel.split("/", 1)[0] if rel.startswith(("en/", "es/")) else "pt"


def visible_stamp(lang: str, date: dt.date) -> str:
    m = MONTHS[lang][date.month - 1]
    if lang == "en":
        label, text = "Updated on", f"{m} {date.day}, {date.year}"
    elif lang == "es":
        label, text = "Actualizado el", f"{date.day} de {m} de {date.year}"
    else:
        label, text = "Atualizado em", f"{date.day} de {m} de {date.year}"
    return (f'<p class="ec-updated" style="max-width:1100px;margin:28px auto 8px;padding:0 20px;'
            f'font-size:13px;line-height:1.5;text-align:center">{label} '
            f'<time datetime="{date.isoformat()}">{text}</time> · Embaixada Carioca</p>')


def url_of(rel: str) -> str:
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[: -len("index.html")]
    return SITE + "/" + rel


def page_nodes(data):
    """Nós do tipo página (WebPage, Article…) no JSON-LD, inclusive dentro de @graph."""
    found = []

    def walk(o, top):
        if isinstance(o, dict):
            t = o.get("@type")
            types = t if isinstance(t, list) else [t]
            if top and any(x in PAGE_TYPES for x in types):
                found.append(o)
            for k, v in o.items():
                walk(v, top and k == "@graph")
        elif isinstance(o, list):
            for v in o:
                walk(v, top)

    walk(data, True)
    return found


def stamp_jsonld(html: str, rel: str, title: str, date: dt.date) -> tuple[str, bool]:
    iso = date.isoformat()
    touched = False
    out, last = [], 0
    for m in JSONLD_RE.finditer(html):
        try:
            data = json.loads(m.group(2))
        except json.JSONDecodeError:
            continue
        nodes = page_nodes(data)
        if not nodes:
            continue
        for n in nodes:
            n["dateModified"] = iso
        raw = m.group(2)
        pretty = "\n" in raw.strip()
        body = json.dumps(data, ensure_ascii=False, indent=2 if pretty else None,
                          separators=None if pretty else (",", ":")).replace("</", "<\\/")
        # Mantém o espaçamento original do bloco (outros geradores comparam o texto).
        lead = raw[: len(raw) - len(raw.lstrip())]
        tail = raw[len(raw.rstrip()):]
        out.append(html[last:m.start(2)] + lead + body + tail)
        last = m.end(2)
        touched = True
    html = "".join(out) + html[last:]
    if touched:
        return html, True
    node = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": url_of(rel) + "#webpage",
        "url": url_of(rel),
        "name": title,
        "inLanguage": LANG_CODE[lang_of(rel)],
        "isPartOf": {"@id": SITE + "/#website"},
        "dateModified": iso,
    }
    block = '<script type="application/ld+json">\n' + json.dumps(node, ensure_ascii=False, indent=2) + "\n</script>\n"
    return html.replace("</head>", block + "</head>", 1), True


def stamp_visible(html: str, rel: str, date: dt.date) -> str:
    stamp = visible_stamp(lang_of(rel), date)
    html = re.sub(STAMP_RE.pattern + r"\n?", "", html, count=1)
    # Dentro de uma landmark: no fim de <main> ou, sem <main>, no começo do rodapé.
    k = html.rfind("</main>")
    # Antes do bloco de links gerado por apply_growth_p1_p2.py, que ele recoloca logo antes de </main>.
    growth = html.rfind("<!-- growth-p1-p2:start -->", 0, k if k >= 0 else len(html))
    if k >= 0 and growth >= 0 and html.rfind("<main", 0, k) < growth:
        k = growth
    if k < 0:
        m = re.search(r"<footer[^>]*>", html)
        k = m.end() if m else html.rfind("</body>")
    return html[:k] + stamp + "\n" + html[k:]


def sitemap_pages() -> list[str]:
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    rels = []
    for loc in re.findall(r"<loc>" + re.escape(SITE) + r"(/[^<]*)</loc>", sm):
        rel = loc.lstrip("/")
        rel = rel + "index.html" if (rel == "" or rel.endswith("/")) else rel
        rels.append(rel)
    return rels


def update_sitemap(rels: list[str], date: dt.date) -> None:
    path = ROOT / "sitemap.xml"
    sm = path.read_text(encoding="utf-8")
    for rel in rels:
        loc = re.escape(url_of(rel))
        sm = re.sub(r"(<loc>" + loc + r"</loc>\s*<lastmod>)[^<]*(</lastmod>)", r"\g<1>" + date.isoformat() + r"\2", sm)
    path.write_text(sm, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="AAAA-MM-DD (padrão: hoje)")
    ap.add_argument("--check", action="store_true", help="lista páginas sem data visível ou sem dateModified")
    ap.add_argument("pages", nargs="*")
    args = ap.parse_args()
    rels = args.pages or sitemap_pages()
    if args.check:
        missing = []
        for rel in rels:
            html = (ROOT / rel).read_text(encoding="utf-8")
            if not STAMP_RE.search(html) or '"dateModified"' not in html:
                missing.append(rel)
        print(f"{len(rels) - len(missing)}/{len(rels)} páginas com data visível e dateModified")
        for rel in missing:
            print("  sem data:", rel)
        return 1 if missing else 0
    date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    for rel in rels:
        path = ROOT / rel
        html = path.read_text(encoding="utf-8")
        title_m = re.search(r"<title[^>]*>([\s\S]*?)</title>", html)
        title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else rel
        html, _ = stamp_jsonld(html, rel, title, date)
        html = stamp_visible(html, rel, date)
        path.write_text(html, encoding="utf-8")
    update_sitemap(rels, date)
    print(f"{len(rels)} páginas marcadas com {date.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

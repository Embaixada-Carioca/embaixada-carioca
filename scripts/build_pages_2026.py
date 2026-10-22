#!/usr/bin/env python3
"""Gera as páginas internas no design 2026 a partir de content/pages/.

Cada página tem um arquivo de conteúdo em content/pages/<caminho>.html:

    <!--page
    { ...JSON com título, descrição, hero, fatos, FAQ e JSON-LD... }
    -->
    <section class="visit-section is-paper">...</section>

O script monta a página completa (head, menu, rodapé, scripts) com a mesma estrutura
da home e do guia "Planeje sua visita" e grava em <caminho>.html na raiz do site.

Uso:
  python3 scripts/build_pages_2026.py              # todas as páginas de content/pages
  python3 scripts/build_pages_2026.py cardapio.html en/cardapio.html
  python3 scripts/build_pages_2026.py --check      # falha se alguma página difere do gerado

Depois de gerar, rode na ordem: scripts/apply_growth_p1_p2.py (bloco de links e meta das
páginas de crescimento) e scripts/stamp_page_dates.py --date AAAA-MM-DD <páginas> (data
visível e dateModified). O --check compara só o miolo gerado por este script.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "pages"
SITE = "https://www.embaixadacarioca.com"
CSS_VERSION = "20261021"
EXT_ATTRS = ' target="_blank" rel="noopener"'
TAGME = "https://go.tagme.com.br/embaixadacarioca"
ADDRESS_HTML = ('<address class="footer-address">Embaixada Carioca<br>Morro da Urca · Parque Bondinho Pão de Açúcar<br>'
                'Av. Pasteur, 520 · Urca · Rio de Janeiro · RJ · 22290-240</address>')
WHATSAPP = "https://wa.me/5521966837556"

LANG = {
    "pt": {
        "html": "pt-BR", "og": "pt_BR", "main": "conteudo-principal",
        "skip": "Pular para o conteúdo principal", "nav_label": "Navegação principal",
        "home": "/", "home_label": "Embaixada Carioca — início", "open_menu": "Abrir menu",
        "languages": "Idiomas", "reserve": "Reservar", "quick": "Ações rápidas",
        "breadcrumb": "Trilha de navegação", "start": "Início",
        "nav": [("/cafe-da-manha.html", "cafe_da_manha", "Café da manhã"), ("/almoco.html", "almoco", "Almoço"),
                ("/cardapio.html", "cardapio", "Cardápio"), ("/eventos.html", "eventos", "Eventos"),
                ("/como-chegar.html", "como_chegar", "Como chegar")],
        "mobile": [("/cardapio.html", "cardapio", "Cardápio"), ("/como-chegar.html", "como_chegar", "Como chegar")],
        "footer_about": "Restaurante no Morro da Urca, dentro do Parque Bondinho Pão de Açúcar, no Rio de Janeiro.",
        "footer_cols": [
            ("Planeje", [("/planeje-sua-visita.html", "Guia da visita"), ("/como-chegar.html", "Como chegar"), ("/cardapio.html", "Cardápio"), (TAGME, "Reservas")]),
            ("Experiências", [("/cafe-da-manha.html", "Café da manhã"), ("/almoco.html", "Almoço"), ("/feijoada.html", "Feijoada"), ("/entardecer.html", "Entardecer"), ("/eventos.html", "Eventos")]),
            ("Contato", [(WHATSAPP, "+55 21 96683-7556"), ("mailto:eventos@embaixadacarioca.com.br", "eventos@embaixadacarioca.com.br"), ("https://www.instagram.com/embaixadacarioca/", "Instagram"), ("/contato.html", "Fale conosco")]),
        ],
        "privacy": "Política de privacidade", "faq_eyebrow": "Perguntas frequentes",
        "about": ("/nossa-visao.html", "Sobre a casa"), "address_label": "Endereço",
    },
    "en": {
        "html": "en", "og": "en_US", "main": "main-content",
        "skip": "Skip to main content", "nav_label": "Main navigation",
        "home": "/en/", "home_label": "Embaixada Carioca — home", "open_menu": "Open menu",
        "languages": "Languages", "reserve": "Reserve", "quick": "Quick actions",
        "breadcrumb": "Breadcrumb", "start": "Home",
        "nav": [("/en/cafe-da-manha.html", "cafe_da_manha", "Breakfast"), ("/en/almoco.html", "almoco", "Lunch"),
                ("/en/cardapio.html", "cardapio", "Menu"), ("/en/eventos.html", "eventos", "Events"),
                ("/en/how-to-get-there.html", "como_chegar", "Getting there")],
        "mobile": [("/en/cardapio.html", "cardapio", "Menu"), ("/en/how-to-get-there.html", "como_chegar", "Getting there")],
        "footer_about": "Restaurant on Urca Hill (Morro da Urca), inside Bondinho Pão de Açúcar Park, Rio de Janeiro.",
        "footer_cols": [
            ("Plan", [("/en/plan-your-visit.html", "Visit guide"), ("/en/how-to-get-there.html", "Getting there"), ("/en/cardapio.html", "Menu"), (TAGME, "Reservations")]),
            ("Experiences", [("/en/cafe-da-manha.html", "Breakfast"), ("/en/almoco.html", "Lunch"), ("/en/feijoada.html", "Feijoada"), ("/en/sunset.html", "Sunset"), ("/en/eventos.html", "Events")]),
            ("Contact", [(WHATSAPP, "+55 21 96683-7556"), ("mailto:eventos@embaixadacarioca.com.br", "eventos@embaixadacarioca.com.br"), ("https://www.instagram.com/embaixadacarioca/", "Instagram"), ("/en/contato.html", "Contact us")]),
        ],
        "privacy": "Privacy policy", "faq_eyebrow": "FAQ",
        "about": ("/en/nossa-visao.html", "About us"), "address_label": "Address",
    },
    "es": {
        "html": "es", "og": "es_ES", "main": "contenido-principal",
        "skip": "Saltar al contenido principal", "nav_label": "Navegación principal",
        "home": "/es/", "home_label": "Embaixada Carioca — inicio", "open_menu": "Abrir menú",
        "languages": "Idiomas", "reserve": "Reservar", "quick": "Acciones rápidas",
        "breadcrumb": "Ruta de navegación", "start": "Inicio",
        "nav": [("/es/cafe-da-manha.html", "cafe_da_manha", "Desayuno"), ("/es/almoco.html", "almoco", "Almuerzo"),
                ("/es/cardapio.html", "cardapio", "Menú"), ("/es/eventos.html", "eventos", "Eventos"),
                ("/es/como-llegar.html", "como_chegar", "Cómo llegar")],
        "mobile": [("/es/cardapio.html", "cardapio", "Menú"), ("/es/como-llegar.html", "como_chegar", "Cómo llegar")],
        "footer_about": "Restaurante en el Morro da Urca, dentro del Parque Bondinho Pão de Açúcar, en Río de Janeiro.",
        "footer_cols": [
            ("Planifica", [("/es/planifica-tu-visita.html", "Guía de la visita"), ("/es/como-llegar.html", "Cómo llegar"), ("/es/cardapio.html", "Menú"), (TAGME, "Reservas")]),
            ("Experiencias", [("/es/cafe-da-manha.html", "Desayuno"), ("/es/almoco.html", "Almuerzo"), ("/es/feijoada.html", "Feijoada"), ("/es/atardecer.html", "Atardecer"), ("/es/eventos.html", "Eventos")]),
            ("Contacto", [(WHATSAPP, "+55 21 96683-7556"), ("mailto:eventos@embaixadacarioca.com.br", "eventos@embaixadacarioca.com.br"), ("https://www.instagram.com/embaixadacarioca/", "Instagram"), ("/es/contato.html", "Contacto")]),
        ],
        "privacy": "Política de privacidad", "faq_eyebrow": "Preguntas frecuentes",
        "about": ("/es/nossa-visao.html", "Sobre la casa"), "address_label": "Dirección",
    },
}

GA4 = ("<script id=\"ec-ga4-base\">window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}"
       "window.ecLoadGA4=window.ecLoadGA4||function(){if(window.ecGA4Loaded)return;window.ecGA4Loaded=true;"
       "var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id=G-9GRXVZ55CB';"
       "document.head.appendChild(s);gtag('js',new Date());gtag('config','G-9GRXVZ55CB',{send_page_view:true})};"
       "(function(){var l=window.ecLoadGA4;['pointerdown','keydown','touchstart','scroll'].forEach(function(e){window.addEventListener(e,l,{once:true,passive:true})});"
       "window.addEventListener('load',function(){'requestIdleCallback'in window?requestIdleCallback(l,{timeout:2200}):setTimeout(l,1400)},{once:true})})();</script>")

LANG_NAMES = (("pt-BR", "Português", "/"), ("en", "English", "/en/"), ("es", "Español", "/es/"))

# Aviso para quem chega com o navegador em outro idioma do site: oferece a versão equivalente.
LANG_OFFER_JS = """<script>
(function(){
  try { if (localStorage.getItem('ec-lang-offer') === 'off') return; } catch (e) {}
  var page = (document.documentElement.lang || '').slice(0, 2).toLowerCase();
  var prefs = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || '']);
  var want = null;
  for (var i = 0; i < prefs.length; i++) { var l = (prefs[i] || '').slice(0, 2).toLowerCase(); if (l === 'pt' || l === 'en' || l === 'es') { want = l; break; } }
  if (!want || want === page) return;
  var alt = document.querySelector('link[rel="alternate"][hreflang^="' + want + '"]');
  if (!alt) return;
  var T = { pt: ['Esta página também existe em português.', 'Ver em português', 'Fechar'], en: ['This page is also available in English.', 'View in English', 'Dismiss'], es: ['Esta página también está disponible en español.', 'Ver en español', 'Cerrar'] }[want];
  var box = document.createElement('div'); box.className = 'lang-offer'; box.setAttribute('role', 'region'); box.setAttribute('lang', want === 'pt' ? 'pt-BR' : want); box.setAttribute('aria-label', T[0]);
  box.innerHTML = '<span>' + T[0] + '</span><a class="button button-small" href="' + alt.getAttribute('href') + '" hreflang="' + alt.getAttribute('hreflang') + '">' + T[1] + '</a><button type="button" class="lang-offer-close" aria-label="' + T[2] + '">\u00d7</button>';
  function off(){ try { localStorage.setItem('ec-lang-offer', 'off'); } catch (e) {} }
  box.querySelector('button').addEventListener('click', function(){ box.remove(); off(); });
  box.querySelector('a').addEventListener('click', off);
  document.body.appendChild(box);
})();
</script>"""

MENU_JS = """<script>
(function(){
  var topbar = document.getElementById('topbar');
  var toggle = document.getElementById('menu-toggle');
  var links = document.getElementById('primary-links');
  function closeMenu(){ toggle.setAttribute('aria-expanded', 'false'); links.classList.remove('is-open'); }
  toggle.addEventListener('click', function(){ var open = toggle.getAttribute('aria-expanded') === 'true'; toggle.setAttribute('aria-expanded', String(!open)); links.classList.toggle('is-open', !open); });
  links.addEventListener('click', function(event){ if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', function(event){ if (event.key === 'Escape') closeMenu(); });
  function onScroll(){ topbar.classList.toggle('is-scrolled', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
})();
</script>"""

FRONT = re.compile(r"^\s*<!--page\s*(\{.*?\})\s*-->\s*", re.S)
GEN_START, GEN_END = "<!-- page-2026:start -->", "<!-- page-2026:end -->"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def lang_of(rel: str) -> str:
    return rel.split("/", 1)[0] if rel.startswith(("en/", "es/")) else "pt"


def url_of(path: str) -> str:
    return SITE + path


def public_path(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def growth_rows() -> dict:
    """Título, descrição, H1 e abertura das páginas de crescimento (fonte: apply_growth_p1_p2.py)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import apply_growth_p1_p2 as growth  # noqa: E402
    rows = {}
    for group in list(growth.GROUPS.values()) + [growth.EXTRAS]:
        for rel, title, desc, h1, lead in group:
            rows[rel] = {"title": title, "description": desc, "h1": h1, "lead": lead}
    return rows


GROWTH = None


def load(rel: str) -> tuple[dict, str]:
    global GROWTH
    raw = (CONTENT / rel).read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        raise SystemExit(f"{rel}: falta o bloco <!--page {{...}} -->")
    meta = json.loads(m.group(1))
    if GROWTH is None:
        GROWTH = growth_rows()
    row = GROWTH.get(rel)
    if row:
        # As páginas de crescimento têm título, descrição, H1 e abertura definidos em apply_growth_p1_p2.py.
        meta["title"], meta["description"] = row["title"], row["description"]
        if row["h1"]:
            meta["hero"]["h1"] = row["h1"]
        if row["lead"]:
            meta["hero"]["lead"] = html.escape(row["lead"])
    return meta, raw[m.end():].strip()


RESTAURANT_DESC = {
    "pt": "Restaurante de cozinha brasileira no Morro da Urca, dentro do Parque Bondinho Pão de Açúcar, com café da manhã, almoço e drinks com vista.",
    "en": "Brazilian restaurant on Urca Hill, inside Bondinho Pão de Açúcar Park, serving breakfast, lunch and drinks with a view of Sugarloaf Mountain.",
    "es": "Restaurante de cocina brasileña en el Morro da Urca, dentro del Parque Bondinho Pão de Açúcar, con desayuno, almuerzo y bebidas con vista.",
}


def restaurant_node(lang: str) -> dict:
    """Entidade do restaurante, a mesma da home (index.html), com descrição no idioma da página."""
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>([\s\S]*?)</script>', home):
        data = json.loads(block)
        for node in data.get("@graph", [data]):
            if node.get("@type") == "Restaurant":
                node = dict(node)
                node["description"] = RESTAURANT_DESC[lang]
                return node
    raise SystemExit("Restaurant não encontrado em index.html")


def schema(meta: dict, rel: str, lang: str) -> list:
    """JSON-LD padronizado: Restaurant, WebSite, WebPage, BreadcrumbList, FAQPage e extras da página."""
    L = LANG[lang]
    canonical = url_of(public_path(rel))
    page_id = canonical + "#webpage"
    crumbs = [{"@type": "ListItem", "position": 1, "name": L["start"], "item": url_of(L["home"])}]
    for i, (name, href) in enumerate(meta["hero"].get("breadcrumbs", []), start=2):
        crumbs.append({"@type": "ListItem", "position": i, "name": name, "item": url_of(href)})
    page = {"@type": meta.get("page_type", "WebPage"), "@id": page_id, "url": canonical, "name": meta["title"],
            "description": meta["description"], "inLanguage": L["html"], "isPartOf": {"@id": SITE + "/#website"},
            "about": {"@id": SITE + "/#restaurant"}, "breadcrumb": {"@id": canonical + "#breadcrumb"},
            "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["h1", ".visit-hero-copy", ".direct-answer"]}}
    if meta["hero"].get("image"):
        page["primaryImageOfPage"] = url_of(meta["hero"]["image"]["src"])
    # Mantém a data gravada por stamp_page_dates.py ao regenerar a página.
    existing = ROOT / rel
    if existing.exists():
        old_text = existing.read_text(encoding="utf-8")
        m = re.search(r'"datePublished":\s*"([^"]+)"', old_text)
        if m:
            page["datePublished"] = m.group(1)
        m = re.search(r'"dateModified":\s*"([^"]+)"', old_text)
        if m:
            page["dateModified"] = m.group(1)
    page["author"] = {"@id": SITE + "/#restaurant"}
    page["publisher"] = {"@id": SITE + "/#restaurant"}
    graph = [restaurant_node(lang),
             {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Embaixada Carioca",
              "inLanguage": L["html"], "publisher": {"@id": SITE + "/#restaurant"}},
             page,
             {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": crumbs}]
    faq = meta.get("faq")
    if faq and faq.get("items"):
        graph.append({"@type": "FAQPage", "@id": canonical + "#faq", "isPartOf": {"@id": page_id},
                      "mainEntity": [{"@type": "Question", "name": q,
                                      "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}}
                                     for q, a in faq["items"]]})
    if meta.get("menu"):
        graph.append({"@type": "Menu", "@id": canonical + "#menu"})  # preenchido por refresh_menu_highlights.py
    graph.extend(meta.get("schema_extra", []))
    return [{"@context": "https://schema.org", "@graph": graph}]


def responsive_variant(webp: str):
    """Versão de 800 px gerada por scripts/make_responsive_images.py, quando existir."""
    if not webp or not webp.endswith(".webp"):
        return None
    candidate = webp[:-5] + "-800w.webp"
    return candidate if (ROOT / candidate.lstrip("/")).exists() else None


def markdown_path(path: str) -> str:
    """URL da versão em Markdown: / -> /index.md, /x.html -> /x.md, /en/ -> /en/index.md."""
    if path.endswith("/"):
        return path + "index.md"
    return re.sub(r"\.html$", ".md", path)


def picture(img: dict, *, eager: bool = False, cls: str = "") -> str:
    src = img["src"]
    width, height = img.get("width"), img.get("height")
    size = f' width="{width}" height="{height}"' if width and height else ""
    loading = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    webp = img.get("webp")
    if not webp and src.endswith((".jpg", ".jpeg", ".png")):
        candidate = re.sub(r"\.(jpe?g|png)$", ".webp", src)
        if (ROOT / candidate.lstrip("/")).exists():
            webp = candidate
    small = responsive_variant(webp) if webp else None
    if webp and webp != src and small:
        source = (f'<source type="image/webp" srcset="{esc(small)} 800w, {esc(webp)} {width or 1280}w" '
                  f'sizes="{"100vw" if eager else "(min-width: 900px) 50vw, 100vw"}">')
    else:
        source = f'<source type="image/webp" srcset="{esc(webp)}">' if webp and webp != src else ""
    klass = f' class="{cls}"' if cls else ""
    img_srcset = ""
    if not source and src.endswith(".webp") and responsive_variant(src):
        img_srcset = (f' srcset="{esc(responsive_variant(src))} 800w, {esc(src)} {width or 1280}w"'
                      f' sizes="{"100vw" if eager else "(min-width: 900px) 50vw, 100vw"}"')
    return f'<picture{klass}>{source}<img src="{esc(src)}"{img_srcset}{size} alt="{esc(img.get("alt", ""))}"{loading}></picture>'


def render_head(meta: dict, rel: str, lang: str) -> str:
    L = LANG[lang]
    path = public_path(rel)
    canonical = url_of(path)
    title, desc = meta["title"], meta["description"]
    image = url_of(meta.get("og_image") or meta["hero"]["image"]["src"])
    robots = meta.get("robots", "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1")
    alts = meta.get("alternates", {})
    alt_links = "".join(f'<link rel="alternate" hreflang="{k}" href="{esc(url_of(v))}">' for k, v in alts.items())
    if alts.get("pt-BR"):
        alt_links += f'<link rel="alternate" hreflang="x-default" href="{esc(url_of(alts["pt-BR"]))}">'
    jsonld = schema(meta, rel, lang)
    blocks = "".join('<script type="application/ld+json">\n' + json.dumps(b, ensure_ascii=False, indent=2).replace("</", "<\\/") + "\n</script>\n" for b in jsonld)
    preload = ""
    hero_img = meta["hero"].get("image")
    if hero_img:
        webp = re.sub(r"\.(jpe?g|png)$", ".webp", hero_img["src"])
        target = webp if (ROOT / webp.lstrip("/")).exists() else hero_img["src"]
        small = responsive_variant(target)
        srcset = f' imagesrcset="{esc(small)} 800w, {esc(target)} {hero_img.get("width", 1280)}w" imagesizes="100vw"' if small else ""
        preload = f'<link rel="preload" as="image" href="{esc(target)}"{srcset} fetchpriority="high">'
    extra_css = "".join(f'<link rel="stylesheet" href="{esc(c)}">' for c in meta.get("css", []))
    md_link = "" if "noindex" in robots else f'\n<link rel="alternate" type="text/markdown" href="{markdown_path(path)}">'
    return f"""<!doctype html>
<html lang="{L['html']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="author" content="Embaixada Carioca">
<meta name="theme-color" content="#00384d">
<link rel="canonical" href="{canonical}">
{alt_links}{md_link}
<meta property="og:type" content="website"><meta property="og:locale" content="{L['og']}"><meta property="og:site_name" content="Embaixada Carioca">
<meta property="og:url" content="{canonical}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{esc(image)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(image)}">
<link rel="icon" href="/assets/icon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/assets/icon-180.png" sizes="180x180">
<link rel="preconnect" href="https://go.tagme.com.br"><link rel="dns-prefetch" href="//bondinho.com.br">
<link rel="preload" href="/assets/fonts/fonts.css" as="style"><link rel="stylesheet" href="/assets/fonts/fonts.css">
{preload}
<link rel="stylesheet" href="/assets/css/ec-home-2026.css?v={CSS_VERSION}"><link rel="stylesheet" href="/assets/css/ec-pages-2026.css?v={CSS_VERSION}"><link rel="stylesheet" href="/assets/css/ec-growth-links.css"/>{extra_css}
{GA4}
{blocks}</head>"""


def render_nav(meta: dict, rel: str, lang: str) -> str:
    L = LANG[lang]
    path = public_path(rel)
    links = []
    for href, intent, label in L["nav"]:
        current = ' aria-current="page"' if href == path else ""
        links.append(f'<a href="{href}" data-intent="{intent}" data-position="nav"{current}>{esc(label)}</a>')
    alts = meta.get("alternates", {})
    langs = []
    for code, short, hl in (("pt-BR", "PT", "pt-BR"), ("en", "EN", "en"), ("es", "ES", "es")):
        target = alts.get(code) or {"pt-BR": "/", "en": "/en/", "es": "/es/"}[code]
        current = ' aria-current="page"' if LANG[lang]["html"] == hl else f' hreflang="{hl}"'
        langs.append(f'<a href="{target}" lang="{hl}"{current}>{short}</a>')
    return (f'<a class="skip-link" href="#{L["main"]}">{esc(L["skip"])}</a>\n'
            f'<nav class="topbar" id="topbar" aria-label="{esc(L["nav_label"])}"><div class="shell nav-shell">'
            f'<a class="brand" href="{L["home"]}" aria-label="{esc(L["home_label"])}"><img src="/assets/logo-areia.svg" width="58" height="58" alt="Embaixada Carioca"></a>'
            f'<button class="menu-toggle" id="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-links"><span class="sr-only">{esc(L["open_menu"])}</span><span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span></button>'
            f'<div class="nav-links" id="primary-links">{"".join(links)}</div>'
            f'<div class="nav-actions"><div class="language-links" aria-label="{esc(L["languages"])}">{"".join(langs)}</div>'
            f'<a class="button button-small" href="{TAGME}" target="_blank" rel="noopener" data-intent="reserva" data-position="nav">{esc(L["reserve"])}</a></div></div></nav>')


def render_hero(meta: dict, lang: str) -> str:
    L = LANG[lang]
    h = meta["hero"]
    crumbs = h.get("breadcrumbs")
    crumb_html = ""
    if crumbs:
        items = [f'<li><a href="{L["home"]}">{esc(L["start"])}</a></li>']
        for c in crumbs[:-1]:
            items.append(f'<li><a href="{esc(c[1])}">{esc(c[0])}</a></li>')
        items.append(f'<li aria-current="page">{esc(crumbs[-1][0])}</li>')
        crumb_html = f'<nav class="visit-breadcrumbs" aria-label="{esc(L["breadcrumb"])}"><ol>{"".join(items)}</ol></nav>'
    actions = []
    for a in h.get("actions", []):
        external = a["href"].startswith("http")
        target = ' target="_blank" rel="noopener"' if external else ""
        klass = "button" if a.get("style", "primary") == "primary" else "button button-outline"
        intent = f' data-intent="{esc(a["intent"])}" data-position="hero"' if a.get("intent") else ""
        form = " data-event-system-link" if "leorangel22.github.io/main/formulario.html" in a["href"] else ""
        actions.append(f'<a class="{klass}" href="{esc(a["href"])}"{target}{intent}{form}>{esc(a["label"])}</a>')
    media = ""
    if h.get("image"):
        media = picture(h["image"], eager=True, cls="visit-hero-media") + '<div class="visit-hero-shade" aria-hidden="true"></div>'
    eyebrow = f'<p class="eyebrow">{esc(h["eyebrow"])}</p>' if h.get("eyebrow") else ""
    return (f'<header class="visit-hero{" page-hero-compact" if h.get("compact") else ""}{"" if h.get("image") else " no-media"}">{media}<div class="shell visit-hero-content">'
            f'{crumb_html}{eyebrow}<h1>{esc(h["h1"])}</h1><p class="visit-hero-copy">{h["lead"]}</p>'
            f'<div class="visit-hero-actions">{"".join(actions)}</div></div></header>')


def render_facts(meta: dict) -> str:
    facts = meta.get("facts")
    if not facts:
        return ""
    cells = "".join(f'<div><strong>{esc(k)}</strong><span>{v}</span></div>' for k, v in facts)
    label = meta.get("facts_label", "")
    aria = f' aria-label="{esc(label)}"' if label else ""
    return f'<section class="decision-strip"{aria}><div class="shell decision-grid">{cells}</div></section>'


def render_faq(meta: dict, lang: str) -> str:
    faq = meta.get("faq")
    if not faq or not faq.get("items"):
        return ""
    L = LANG[lang]
    items = "".join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in faq["items"])
    intro = f'<p>{faq["intro"]}</p>' if faq.get("intro") else ""
    return (f'<section class="visit-section is-paper" id="perguntas" aria-labelledby="faq-title"><div class="shell hub-faq">'
            f'<div><p class="eyebrow eyebrow-dark">{esc(faq.get("eyebrow", L["faq_eyebrow"]))}</p><h2 id="faq-title">{esc(faq["title"])}</h2>{intro}</div>'
            f'<div class="faq-list">{items}</div></div></section>')


def render_footer(lang: str, meta: dict) -> str:
    L = LANG[lang]
    cols = []
    for title, links in L["footer_cols"]:
        anchors = "".join(
            f'<a href="{esc(h)}"{EXT_ATTRS if h.startswith("http") else ""}>{esc(t)}</a>' for h, t in links)
        cols.append(f'<div><h2>{esc(title)}</h2>{anchors}</div>')
    mobile = "".join(f'<a href="{h}" data-intent="{i}" data-position="mobile_bar">{esc(t)}</a>' for h, i, t in L["mobile"])
    event_action = next((a for a in meta.get("hero", {}).get("actions", [])
                         if a.get("href", "").startswith("https://leorangel22.github.io/main/formulario.html?")), None)
    if event_action:
        primary = f'<a class="mobile-reserve" href="{esc(event_action["href"])}" target="_blank" rel="noopener" data-intent="eventos" data-position="mobile_bar" data-event-system-link>{esc(event_action["label"])}</a>'
    else:
        primary = f'<a class="mobile-reserve" href="{TAGME}" target="_blank" rel="noopener" data-intent="reserva" data-position="mobile_bar">{esc(L["reserve"])}</a>'
    alts = meta.get("alternates", {})
    langs = ""
    for code, name, home in LANG_NAMES:
        current = ' aria-current="page"' if code == L["html"] else ""
        langs += f'<a href="{esc(alts.get(code, home))}" lang="{code}" hreflang="{code}"{current}>{name}</a>'
    footer_langs = f'<nav class="footer-langs" aria-label="{esc(L["languages"])}">{langs}</nav>'
    scripts = "".join(f'<script src="{esc(s)}" defer></script>' for s in meta.get("scripts", []))
    return (f'<footer class="footer"><div class="shell footer-grid"><div class="footer-brand"><img src="/assets/logo-areia.svg" width="72" height="72" loading="lazy" alt="Embaixada Carioca"><p>{esc(L["footer_about"])}</p>{ADDRESS_HTML}</div>{"".join(cols)}</div>'
            f'<div class="shell footer-bottom">{footer_langs}<span>© 2026 Embaixada Carioca</span><a href="{L["about"][0]}">{esc(L["about"][1])}</a><a href="/politica-de-privacidade.html">{esc(L["privacy"])}</a></div></footer>\n'
            f'<nav class="mobile-actions" aria-label="{esc(L["quick"])}">{mobile}{primary}</nav>\n'
            f'{MENU_JS}\n{LANG_OFFER_JS}\n<script src="/assets/conversion-tracking.js?v=20261005p2" defer></script><script src="/assets/web-vitals-tracking.js?v=20261005p2" defer></script>{scripts}\n'
            "<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});},{once:true});}</script>\n"
            '<script defer src="/assets/js/ec-a11y-guard.js?v=20261020"></script>')


def render(rel: str) -> str:
    meta, body = load(rel)
    lang = lang_of(rel)
    L = LANG[lang]
    hero = "" if meta.get("custom_hero") else render_hero(meta, lang)
    faq = render_faq(meta, lang)
    if "<!--faq-->" in body:
        body, faq = body.replace("<!--faq-->", faq, 1), ""
    main = (f'<main id="{L["main"]}">\n{GEN_START}\n{hero}\n{render_facts(meta)}\n{body}\n'
            f'{faq}\n{GEN_END}\n</main>')
    page = (render_head(meta, rel, lang) + '\n<body class="page-2026">\n' + render_nav(meta, rel, lang) + "\n" + main + "\n"
            + render_footer(lang, meta) + "\n</body>\n</html>\n")
    if meta.get("menu"):
        # Seções do cardápio e nó Menu do JSON-LD vêm de refresh_menu_highlights.py (preços conferidos).
        sys.path.insert(0, str(ROOT / "scripts"))
        from refresh_menu_highlights import refresh_menu  # noqa: E402
        page = refresh_menu(page, lang)
    return page


def generated_core(text: str) -> str:
    """Trecho gerado por este script, sem o que os outros geradores acrescentam."""
    a, b = text.find(GEN_START), text.find(GEN_END)
    body = text[a:b] if a >= 0 and b > a else ""
    head = [m.group(0) for pat in (r"<title>.*?</title>", r'<meta name="description" content="[^"]*">',
                                   r'<link rel="canonical" href="[^"]*">')
            for m in [re.search(pat, text, re.S)] if m]
    return "\n".join(head) + body


def merge_existing(rel: str, fresh: str) -> str:
    """Preserva o que apply_growth_p1_p2 e stamp_page_dates acrescentam ao fim de <main>."""
    path = ROOT / rel
    if not path.exists():
        return fresh
    old = path.read_text(encoding="utf-8")
    if GEN_END not in old:
        return fresh
    tail = old[old.find(GEN_END) + len(GEN_END): old.find("</main>")]
    return fresh.replace(GEN_END + "\n</main>", GEN_END + tail + "</main>", 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("pages", nargs="*")
    args = ap.parse_args()
    rels = args.pages or sorted(p.relative_to(CONTENT).as_posix() for p in CONTENT.rglob("*.html"))
    bad = []
    for rel in rels:
        fresh = render(rel)
        if args.check:
            current = (ROOT / rel).read_text(encoding="utf-8") if (ROOT / rel).exists() else ""
            if generated_core(current) != generated_core(fresh):
                bad.append(rel)
            continue
        (ROOT / rel).write_text(merge_existing(rel, fresh), encoding="utf-8")
    if args.check:
        if bad:
            print("Páginas 2026 desatualizadas:", ", ".join(bad))
            return 1
        print(f"Páginas 2026: PASS ({len(rels)} páginas)")
        return 0
    print(f"{len(rels)} páginas geradas no design 2026")
    return 0


if __name__ == "__main__":
    sys.exit(main())

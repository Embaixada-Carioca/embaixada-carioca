/*
 * ec-a11y-guard.js — correções de acessibilidade aplicadas em todas as páginas (20/10/2026).
 *
 * Por quê: as folhas antigas forçam texto creme dentro de <main> (regra "HARD READABILITY FIX")
 * e muitos cartões claros herdam essa cor; menus fechados com aria-hidden continuam com links
 * focáveis; seções ficam fora de landmarks. Corrigir página por página exigiria reescrever ~70
 * arquivos com CSS próprio. Este script mede o que o visitante vê e corrige só o que falha:
 *
 * 1. Contraste: texto abaixo de 4,5:1 (3:1 se grande) recebe a cor da marca que passa sobre o
 *    fundo real (azul #00405a, marrom #7a5000, creme #f6efde ou amarelo #f5c842).
 * 2. Menus ocultos (aria-hidden="true"): itens saem da ordem de tabulação até o menu abrir.
 * 3. Landmarks: blocos de conteúdo fora de main/header/footer/nav viram região nomeada;
 *    <aside> dentro de outra landmark vira nota; links de pular conteúdo ganham destino.
 * 4. Áreas com rolagem horizontal recebem foco pelo teclado.
 * 5. Links dentro de parágrafos sem sublinhado e sem contraste com o texto ganham sublinhado.
 */
(function () {
  'use strict';
  if (window.ecA11yGuard) return;
  window.ecA11yGuard = true;

  var doc = document;
  var lang = (doc.documentElement.getAttribute('lang') || 'pt').slice(0, 2).toLowerCase();
  var TEXT = {
    pt: { region: 'Conteúdo', scroll: 'Conteúdo com rolagem horizontal', wa: 'WhatsApp' },
    en: { region: 'Content', scroll: 'Horizontally scrolling content', wa: 'WhatsApp' },
    es: { region: 'Contenido', scroll: 'Contenido con desplazamiento horizontal', wa: 'WhatsApp' }
  }[lang] || { region: 'Conteúdo', scroll: 'Conteúdo com rolagem horizontal', wa: 'WhatsApp' };

  /* ---------- cores ---------- */
  function parseColor(value) {
    var m = /rgba?\(([^)]+)\)/.exec(value || '');
    if (!m) return null;
    var p = m[1].split(/[\s,\/]+/).filter(Boolean).map(parseFloat);
    if (p.length < 3 || p.some(isNaN)) return null;
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function hex(h) { return { r: parseInt(h.slice(1, 3), 16), g: parseInt(h.slice(3, 5), 16), b: parseInt(h.slice(5, 7), 16), a: 1 }; }
  function blend(top, bottom) {
    var a = top.a + bottom.a * (1 - top.a);
    if (a <= 0) return { r: 0, g: 0, b: 0, a: 0 };
    function ch(k) { return (top[k] * top.a + bottom[k] * bottom.a * (1 - top.a)) / a; }
    return { r: ch('r'), g: ch('g'), b: ch('b'), a: a };
  }
  function lum(c) {
    function f(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function isWarm(c) {
    var r = c.r / 255, g = c.g / 255, b = c.b / 255, max = Math.max(r, g, b), min = Math.min(r, g, b);
    if (max - min < 0.25) return false;
    var h;
    if (max === r) h = ((g - b) / (max - min)) % 6; else if (max === g) h = (b - r) / (max - min) + 2; else h = (r - g) / (max - min) + 4;
    h *= 60; if (h < 0) h += 360;
    return h >= 15 && h <= 65;
  }

  var WHITE = { r: 255, g: 255, b: 255, a: 1 };
  var MEDIA = /^(IMG|VIDEO|PICTURE|CANVAS|SVG|IFRAME|OBJECT|EMBED)$/i;

  /* Fundo efetivo atrás do elemento: pilha visual no ponto do texto (como o axe), senão ancestrais. */
  function layersFrom(list) {
    var layers = [];
    for (var i = 0; i < list.length; i++) {
      var n = list[i];
      if (n === doc.documentElement) break;
      if (MEDIA.test(n.tagName)) return null;
      var cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      var c = parseColor(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    var bg = WHITE;
    for (var j = layers.length - 1; j >= 0; j--) bg = blend(layers[j], bg);
    return bg;
  }
  function backgroundOf(el, usePoint) {
    if (usePoint && doc.elementsFromPoint) {
      var rects = el.getClientRects();
      if (rects.length) {
        var r = rects[0];
        var x = r.left + Math.min(r.width / 2, 8), y = r.top + r.height / 2;
        if (x >= 0 && y >= 0 && x < innerWidth && y < innerHeight) {
          var stack = doc.elementsFromPoint(x, y);
          var at = stack.indexOf(el);
          if (at >= 0) return layersFrom(stack.slice(at));
        }
      }
    }
    var chain = [];
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) chain.push(n);
    return layersFrom(chain);
  }
  /* Barras fixas mudam de cor com a rolagem: não recebem cor fixa. */
  function inFixedBar(el) {
    for (var n = el; n && n !== doc.body; n = n.parentElement) {
      var pos = getComputedStyle(n).position;
      if (pos === 'fixed' || pos === 'sticky') return true;
    }
    return false;
  }

  function ownText(el) {
    for (var c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3 && /\S/.test(c.nodeValue)) return true;
    return false;
  }
  function opacityOf(el) {
    var o = 1;
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity) || 0;
    return o;
  }

  var DARK_BG = ['#f6efde', '#ffffff'], DARK_BG_WARM = ['#f5c842', '#f6efde', '#ffffff'];
  var LIGHT_BG = ['#00405a', '#1f2a2e', '#000000'], LIGHT_BG_WARM = ['#7a5000', '#5c3c00', '#00405a', '#000000'];

  function trace(el, msg) { if (window.__ecA11yTrace && el.matches && el.matches(window.__ecA11yTrace)) console.log('[a11y-guard]', msg); }
  function checkContrast(el, tries, usePoint) {
    trace(el, 'check try=' + tries + ' y=' + Math.round(el.getBoundingClientRect().top));
    if (!el.isConnected || el.hasAttribute('data-ec-contrast') || el.closest('svg, [aria-hidden="true"], .sr-only, .visually-hidden')) return;
    if (inFixedBar(el)) return;
    var cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    var fg = parseColor(cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color ? cs.webkitTextFillColor : cs.color);
    if (!fg) return;
    var op = opacityOf(el);
    if (op < 0.95) {
      /* Entrando com animação: mede de novo quando terminar. */
      if (tries < 6) setTimeout(function () { checkContrast(el, tries + 1, usePoint); }, 900);
      return;
    }
    var bg = backgroundOf(el, usePoint);
    if (!bg) { trace(el, 'no bg'); return; }
    var size = parseFloat(cs.fontSize) || 16, weight = parseInt(cs.fontWeight, 10) || 400;
    var need = (size >= 24 || (size >= 18.66 && weight >= 700)) ? 3 : 4.5;
    var seen = blend({ r: fg.r, g: fg.g, b: fg.b, a: fg.a * op }, bg);
    trace(el, 'fg=' + JSON.stringify(fg) + ' bg=' + JSON.stringify(bg) + ' op=' + op + ' r=' + ratio(seen, bg).toFixed(2));
    if (ratio(seen, bg) >= need) { el.__ecOk = (el.__ecOk || 0) + 1; return; }
    var light = lum(bg) > 0.18;
    var warm = isWarm(fg);
    var options = light ? (warm ? LIGHT_BG_WARM : LIGHT_BG) : (warm ? DARK_BG_WARM : DARK_BG);
    /* Fundos de tom médio: se nenhuma cor do grupo passar, tenta também o grupo oposto. */
    options = options.concat(light ? DARK_BG : LIGHT_BG);
    var pick = null, best = 0, bestHex = options[0];
    for (var i = 0; i < options.length; i++) {
      var c = hex(options[i]);
      var r = ratio(blend({ r: c.r, g: c.g, b: c.b, a: op }, bg), bg);
      if (r >= need + 0.2 && !pick) pick = options[i];
      if (r > best) { best = r; bestHex = options[i]; }
    }
    var color = pick || bestHex;
    el.style.setProperty('color', color, 'important');
    el.style.setProperty('-webkit-text-fill-color', color, 'important');
    if (!pick && parseFloat(cs.opacity) < 1) el.style.setProperty('opacity', '1', 'important');
    el.setAttribute('data-ec-contrast', 'fixed');
  }

  var textEls = [];
  function watchText(root) {
    var all = (root || doc.body).querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.__ecWatched || /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|svg|path|OPTION)$/i.test(el.tagName)) continue;
      if (!ownText(el)) continue;
      el.__ecWatched = true;
      textEls.push(el);
      if (io) io.observe(el);
    }
  }
  /* Passada completa: a página inteira, inclusive o que está fora da tela. */
  function contrastPass() {
    if (doc.readyState !== 'complete') return;
    for (var i = 0; i < textEls.length; i++) if (!(textEls[i].__ecOk >= 2)) checkContrast(textEls[i], 0, false);
  }
  /* Ao entrar na tela, mede de novo com a pilha visual real (mais precisa que os ancestrais). */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target;
      io.unobserve(el);
      checkContrast(el, 1, true);
      /* Animações de entrada: mede de novo quando terminarem. */
      setTimeout(function () { checkContrast(el, 2, true); }, 900);
      setTimeout(function () { checkContrast(el, 3, true); }, 2200);
    });
  }) : null;

  /* ---------- menus ocultos ---------- */
  var FOCUSABLE = 'a[href], button, input, select, textarea, summary, [tabindex], [contenteditable="true"]';
  function syncHidden(container) {
    var hidden = container.getAttribute('aria-hidden') === 'true';
    var items = container.querySelectorAll(FOCUSABLE);
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      if (hidden) {
        if (!it.hasAttribute('data-ec-tabindex')) it.setAttribute('data-ec-tabindex', it.hasAttribute('tabindex') ? it.getAttribute('tabindex') : '');
        it.setAttribute('tabindex', '-1');
      } else if (it.hasAttribute('data-ec-tabindex')) {
        var old = it.getAttribute('data-ec-tabindex');
        if (old === '') it.removeAttribute('tabindex'); else it.setAttribute('tabindex', old);
        it.removeAttribute('data-ec-tabindex');
      }
    }
  }
  function syncAllHidden() {
    var list = doc.querySelectorAll('[aria-hidden]');
    for (var i = 0; i < list.length; i++) if (list[i].querySelector(FOCUSABLE)) syncHidden(list[i]);
  }

  /* ---------- landmarks ---------- */
  var LANDMARK = 'main, [role="main"], header, [role="banner"], footer, [role="contentinfo"], nav, [role="navigation"], aside, [role="complementary"], [role="search"], section[aria-label], section[aria-labelledby], [role="region"][aria-label], [role="region"][aria-labelledby], form[aria-label], form[aria-labelledby]';
  var usedLabels = {};
  function uniqueLabel(text) {
    var base = (text || TEXT.region).replace(/\s+/g, ' ').trim().slice(0, 80) || TEXT.region;
    var label = base, n = 2;
    while (usedLabels[label]) label = base + ' (' + (n++) + ')';
    usedLabels[label] = true;
    return label;
  }
  function headingText(el) {
    var h = el.querySelector('h1, h2, h3, h4');
    return h ? h.textContent : (el.getAttribute('aria-label') || '');
  }
  function hasContent(el) {
    if (/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|LINK|META)$/.test(el.tagName)) return false;
    if (el.getAttribute('aria-hidden') === 'true' || el.hidden) return false;
    if (/\S/.test(el.textContent) || el.querySelector('img, video, iframe, picture')) {
      var cs = getComputedStyle(el);
      return cs.display !== 'none' && cs.visibility !== 'hidden';
    }
    return false;
  }
  function isSkipLink(el) {
    return el.tagName === 'A' && /skip/i.test(el.className) && (el.getAttribute('href') || '').charAt(0) === '#';
  }
  /* Landmarks que precisam ficar no topo: não podem ir para dentro de uma região. */
  var TOP_LEVEL = 'main, [role="main"], header, [role="banner"], footer, [role="contentinfo"], aside, [role="complementary"]';
  /* Elementos com semântica própria não recebem role. */
  var SEMANTIC = /^(H[1-6]|P|A|UL|OL|LI|DL|TABLE|IMG|BUTTON|INPUT|SELECT|TEXTAREA|LABEL|FIGURE|BLOCKQUOTE|ARTICLE|FORM|DETAILS|SUMMARY|IFRAME|VIDEO|PICTURE)$/;
  function wrapStray(parent) {
    var kids = parent.children;
    for (var i = 0; i < kids.length; i++) {
      var k = kids[i];
      if (k.matches(LANDMARK) || isSkipLink(k) || !hasContent(k)) continue;
      if (k.querySelector(TOP_LEVEL)) { wrapStray(k); continue; }
      if (k.id === 'wa-widget' || getComputedStyle(k).position === 'fixed') {
        if (SEMANTIC.test(k.tagName)) continue;
        k.setAttribute('role', 'complementary');
        k.setAttribute('aria-label', k.getAttribute('aria-label') || (k.id === 'wa-widget' ? TEXT.wa : uniqueLabel(headingText(k))));
        continue;
      }
      if (SEMANTIC.test(k.tagName)) continue;
      if (k.tagName !== 'SECTION') k.setAttribute('role', 'region');
      k.setAttribute('aria-label', uniqueLabel(headingText(k)));
    }
  }
  function fixLandmarks() {
    var labelled = doc.querySelectorAll('[aria-label]');
    for (var i = 0; i < labelled.length; i++) usedLabels[labelled[i].getAttribute('aria-label')] = true;
    wrapStray(doc.body);
    /* <aside> ou complementar dentro de outra landmark vira nota. */
    var asides = doc.querySelectorAll('aside, [role="complementary"]');
    for (var j = 0; j < asides.length; j++) {
      var a = asides[j], up = a.parentElement && a.parentElement.closest(LANDMARK);
      if (up && up !== doc.body) a.setAttribute('role', 'note');
    }
    /* Link "pular para o conteúdo" sem destino aponta para o conteúdo principal. */
    var skips = doc.querySelectorAll('a[href^="#"]');
    for (var s = 0; s < skips.length; s++) {
      var link = skips[s];
      if (!isSkipLink(link)) continue;
      var id = decodeURIComponent(link.getAttribute('href').slice(1));
      if (id && !doc.getElementById(id)) {
        var target = doc.querySelector('main, [role="main"]') || doc.querySelector('h1');
        if (target && !target.id) target.id = id;
        if (target && target.id !== id) link.setAttribute('href', '#' + target.id);
        if (target && !target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      }
      /* O link de pular precisa ser o primeiro link da página. */
      var first = doc.querySelector('a[href]');
      if (first !== link && !(doc.body.firstElementChild === link)) doc.body.insertBefore(link, doc.body.firstChild);
    }
  }

  /* ---------- rolagem horizontal ---------- */
  function fixScrollers() {
    var all = doc.body.querySelectorAll('div, ul, ol, table, section, figure, pre');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.hasAttribute('tabindex')) continue;
      var cs = getComputedStyle(el);
      var sx = /(auto|scroll)/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 2;
      var sy = /(auto|scroll)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 2;
      if (!sx && !sy) continue;
      if (el.querySelector(FOCUSABLE)) continue;
      el.setAttribute('tabindex', '0');
      if (!el.hasAttribute('role') && !/^(TABLE|UL|OL)$/.test(el.tagName)) el.setAttribute('role', 'region');
      if (!el.hasAttribute('aria-label')) el.setAttribute('aria-label', uniqueLabel(headingText(el) || TEXT.scroll));
    }
  }

  /* ---------- links dentro de texto ---------- */
  function fixInlineLinks() {
    var links = doc.querySelectorAll('p a[href], li a[href], td a[href], dd a[href], .wrap > a[href]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i], p = a.parentElement;
      if (!p || a.classList.contains('btn') || /button/.test(a.getAttribute('role') || '')) continue;
      var text = '';
      for (var c = p.firstChild; c; c = c.nextSibling) if (c.nodeType === 3) text += c.nodeValue;
      if (!/\w{3}/.test(text)) continue;
      var cs = getComputedStyle(a), ps = getComputedStyle(p);
      if (/underline/.test(cs.textDecorationLine) || parseFloat(cs.borderBottomWidth) > 0) continue;
      var ca = parseColor(cs.color), cp = parseColor(ps.color);
      if (ca && cp && ratio(ca, cp) >= 3) continue;
      a.style.setProperty('text-decoration', 'underline', 'important');
      a.style.setProperty('text-underline-offset', '2px');
    }
  }

  /* Alvos de toque mínimos (WCAG 2.2, 24 px). */
  function injectCss() {
    if (doc.getElementById('ec-a11y-guard-css')) return;
    var st = doc.createElement('style');
    st.id = 'ec-a11y-guard-css';
    st.textContent = 'details>summary{min-height:24px;padding-block:4px}' +
      '.internal-links li>a{display:inline-block;min-height:24px;padding-block:2px}' +
      '[data-ec-scroll-focus]:focus-visible,[role="region"][tabindex="0"]:focus-visible{outline:3px solid #f59b1e;outline-offset:2px}';
    doc.head.appendChild(st);
  }

  function runStatic() {
    injectCss();
    syncAllHidden();
    fixLandmarks();
    fixScrollers();
    fixInlineLinks();
    watchText();
    contrastPass();
  }

  var pending = null;
  function schedule() {
    if (pending) return;
    pending = setTimeout(function () { pending = null; runStatic(); }, 400);
  }

  function start() {
    runStatic();
    new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var r = records[i];
        if (r.type === 'attributes') { syncHidden(r.target); continue; }
        if (r.addedNodes.length) { schedule(); break; }
      }
    }).observe(doc.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['aria-hidden'] });
    addEventListener('load', schedule);
    /* Depois de cada rolagem, mede de novo o que entrou na tela com animação. */
    var scrollTimer = null;
    addEventListener('scroll', function () { clearTimeout(scrollTimer); scrollTimer = setTimeout(contrastPass, 600); }, { passive: true });
    addEventListener('resize', function () { clearTimeout(window.__ecA11yResize); window.__ecA11yResize = setTimeout(fixScrollers, 300); });
    setTimeout(schedule, 1200);
    setTimeout(schedule, 3000);
  }

  window.ecA11yGuardDebug = { backgroundOf: backgroundOf, check: checkContrast };

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
})();

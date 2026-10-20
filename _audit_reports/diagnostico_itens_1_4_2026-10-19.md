# Lote de correções do diagnóstico — 19/10/2026

Base: branch `fix/seo-fatos-cardapio-20261019` (PR #36, commit `d279891`). Este lote depende do PR #36 e deve ser publicado depois dele.

## 1. Páginas falhando para quem volta ao site (roteador do Cloudflare)

**Causa.** `functions/[[path]].js` repassava a requisição inteira do navegador para a busca do HTML guardado em `_html/`. Quando o navegador ou um rastreador já tinha a página em cache e enviava `If-None-Match`, a busca respondia `304` e a função tratava isso como "página inexistente", devolvendo `404` com corpo vazio. No Chrome isso aparece como `ERR_INVALID_RESPONSE`.

**Evidência em produção (19/10/2026, www.embaixadacarioca.com):** `/`, `/almoco.html` e `/cardapio.html` responderam `200` sem cabeçalho condicional e `404` com 0 bytes com `If-None-Match` igual ao ETag recebido. O mesmo comportamento foi reproduzido localmente com `wrangler pages dev` usando a função original.

**Correção.** Só `If-None-Match` e `If-Modified-Since` chegam à busca interna; `304` é devolvido como `304`; `Range` não é mais repassado. URLs inexistentes pedidas como HTML recebem o `404.html` do site, mantendo o status `404`; arquivos inexistentes continuam com `404` vazio.

**Testes.** `scripts/test_growth_router.mjs` ganhou 9 casos de revalidação e 2 de página não encontrada; os casos falham com a função antiga. No `wrangler pages dev`: revalidação → `304`; ETag diferente → `200`; `Range` → `200`; URL inexistente → `404` com o `404.html`; aliases continuam em `301`.

O domínio sem `www` continua redirecionando corretamente para `www` (9 de 9 testes no Chrome e 4 de 4 por outra rede, em http e https). Nenhuma mudança de DNS foi necessária.

## 2. Feijoada: prêmio atribuído à Academia da Cachaça (PT/EN/ES)

- Título, descrição, Open Graph e Twitter da página PT eram os da página de almoço; título ES trazia "La Mejor Feijoada de Río de Janeiro 4,8★".
- H1 "A Melhor Feijoada do Rio de Janeiro" (e equivalentes EN/ES) e trechos "Nossa feijoada premiada" / "Our award-winning feijoada" / "Nuestra feijoada premiada" foram reescritos para nomear a Academia da Cachaça e a parceria formal.
- JSON-LD: `WebPage`, `mainEntityOfPage`, `@id` e breadcrumb apontavam para `almoco.html`; agora apontam para a própria página de feijoada de cada idioma.
- Disponibilidade confirmada pelo responsável em 20/10/2026: feijoada servida no almoço, até as 17h. Corrigido "no almoço e entardecer" (PT/EN/ES) e removida a feijoada da resposta de FAQ do pôr do sol em `por-do-sol-morro-da-urca.html` (JSON-LD).

## 3. Cardápio PT/EN/ES: layout e contraste

- Novo `assets/css/ec-menu-fixes-2026.css`, carregado só nos três cardápios, dentro de `@layer ec-menu-fixes` (mesmo recurso de `@layer bnav-override`).
- Grade das seções e bloco "Guias principais" contidos em 1100 px.
- Preços, numeração, "Cardápio online", botão "Abrir cardápio completo", título "Fotos do Restaurante" e rótulos sobre faixa azul acima de 4,5:1.
- Script inline `fixMenu`: cor dos preços de `#9a6500` (3,85:1) para `#7a5000` (5,49:1). O mesmo script existe em cerca de 90 outras páginas e não foi alterado neste lote.
- axe-core (WCAG 2.2 AA + boas práticas) nos três cardápios: de 22–31 para 6–8 nós com violação por página/largura; as violações de contraste restantes são falsos positivos do botão "Voltar à Home" sobre fundo azul.

## 4. Texto oculto e blocos de âncoras exatas

- Removido o H2 `#seo-subtitle` oculto (1×1 px, texto transparente) de 7 páginas PT: almoço, cardápio, entardecer, feijoada, guia do Rio, restaurante com vista e pôr do sol.
- Removido o bloco "Guias Rápidos e Destaques Gastronômicos" (`.quick-seo-silo-links`, 5–6 links com âncora de palavra-chave) de 6 páginas PT e das homes EN/ES.
- Consolidação de páginas por variação de busca **não** foi feita neste lote: o cluster de restaurante é intencional (palavras-ouro do GSC e `validate_restaurant_search_cluster.py`) e a decisão depende de dados recentes do Search Console.

## Validação

| Verificação | Resultado |
|---|---|
| `schema_rating_guard.py --check` | PASS, 122 arquivos |
| `schema_jsonld_duplicate_key_guard.py --check` | PASS, 122 arquivos |
| `audit_hreflang_pt_en_es.py` | PASS, nota mínima 100 |
| `validate_i18n_sync.py` | OK |
| `apply_growth_p1_p2.py --check` | PASS |
| `test_growth_router.mjs` | PASS |
| `audit_p2_visit_hub.py` | PASS |
| `build_cloudflare_pages.py` | 527 arquivos |
| `validate_restaurant_search_cluster.py` | FAIL já existente em `master` (ec34d71), sem relação com este lote |
| axe-core nas 14 páginas alteradas, 375 e 1440 px | 973 → 819 nós; nenhuma regra nova; sem rolagem horizontal |

Canonical, hreflang, URLs, preços e `sitemap.xml` não foram alterados.

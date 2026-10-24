# Estado atual do site — Embaixada Carioca

**Atualizado em:** 24/10/2026

**Domínio canônico:** `https://www.embaixadacarioca.com/`

**Repositório:** `Embaixada-Carioca/embaixada-carioca` (antes `LeoRangel22/embaixada-carioca`)

**Branch de produção:** `master`

Este é o documento de referência para o estado operacional atual. Relatórios datados em `_audit_reports/` registram o momento em que foram gerados e podem conter limitações já superadas.

## Estado verificado em 24/10/2026 — crescimento (itens 1–4 do plano de 24/10)

Avaliação de impacto (GSC + GA4, 17–23/10 vs 10–16/10): tráfego humano estável, conversões sem regressão após o design 2026 (click_reservar 73 vs 81 usuários; click_cardapio 143 = 143; whatsapp 11 = 11), ganho de SEO ainda não mensurável com 3 dias. O "+84%" de usuários no GA4 era automação (auditorias Playwright/Lighthouse e previews, Direct de datacenters nos EUA). Baseline GSC para novembro: semana 16–22/10 = 208 cliques / 13.030 impressões / CTR 1,6%.

- PR #51 — medição limpa: `ec-ga4-base` não carrega o gtag quando `navigator.webdriver` é verdadeiro, o user-agent é HeadlessChrome/Lighthouse/bot/crawl/spider ou o hostname não é `embaixadacarioca.com`. Eventos-chave no GA4 já estavam marcados (ec_reservation_click, whatsapp_click, ec_event_lead_outbound). O atalho `go.tagme.com.br/embaixadacarioca` descarta parâmetros no redirecionamento: origem das reservas só pelo relatório da Tagme.
- PR #52 — CTR: parque-bondinho, morro-da-urca e como-chegar (PT/EN/ES) com title/description reescritos e o horário do Parque Bondinho datado (outubro de 2026, fonte bondinho.com.br: seg–sex 8h30–21h, sáb–dom 7h30–21h, último embarque 19h30). Reavaliar o horário a cada temporada.
- PR #53 — prova social: página de avaliações (PT/EN/ES) com seis trechos transcritos de avaliações públicas do Google (primeiro nome · mês), sem Review/AggregateRating no JSON-LD; home PT/EN/ES com link "4,8 no Google" no hero. CSS v20261024, SW `ec-assets-v2026-10-24`.
- PR #54 — barra fixa do celular: o link para a própria página vira WhatsApp (cardápio e como-chegar, PT/EN/ES).
- Próximos itens do plano: formulário curto de eventos (44 cliques no CTA → 4 leads em 28 dias), internacional (medir 2 semanas após PR #47), Meta Ads só com medição limpa.

## Estado verificado em 22/10/2026

- Pacote A: PR #46, commit `88b9c31a9f38fc0f2eb77c7fcf1ba3fc891b6997`, deployment e monitor pós-publicação aprovados. `version.json` público é gerado no build, com SHA real e hashes dos quatro assets críticos. O arquivo histórico da raiz não é mais copiado para produção.
- O monitor verifica oito páginas de forma independente: homes PT/EN/ES, almoço, café da manhã e eventos PT/EN/ES. Um erro não pula os outros idiomas. O postflight compara o SHA com o deployment concluído; o monitor periódico confere manifesto, páginas e hashes, sem afirmar que há uma versão nova quando apenas o Git avançou.
- Inventário estático atual: 70 páginas produzidas pelo builder; 72 URLs no sitemap. Números de auditorias anteriores abaixo são históricos, não novas medições.
- Os relatos de dois cabeçalhos e 23 combinações CSS antecedem a consolidação de 20/10. Não justificam refazer o site. Manter builder e componentes existentes; migração fica para planejamento posterior às férias.
- O gate antigo Pa11y permite até 840 erros de sua baseline histórica. Não interpretar seu verde como zero violações. O novo gate de jornadas em Chromium verifica homes e páginas de eventos em PT/EN/ES, 375 e 1440 px, menu e overflow, com zero violações nas regras axe WCAG selecionadas. Isso não certifica toda a acessibilidade nem as jornadas comerciais externas.
- Nenhum teste submete formulário ou envia mensagens. Reservas reais e operação comercial exigem validação separada. Métricas internas de web-vitals são aproximações, não certificação Core Web Vitals.
- PR #14 permanece separado: alterações antigas de responsive safety lock não foram incorporadas nem sobrescritas por estes pacotes.

## Arquitetura publicada

### Nível A do diagnóstico — 20/10/2026

- `assets/js/ec-a11y-guard.js` roda em todas as páginas PT/EN/ES. Mede o contraste real de cada texto e, abaixo de 4,5:1 (3:1 em texto grande), aplica a cor da marca que passa sobre aquele fundo; tira da ordem de tabulação os links de menus fechados (`aria-hidden="true"`); nomeia blocos fora de landmarks; dá foco a áreas com rolagem; acerta links "pular para o conteúdo". Barras fixas (topo, WhatsApp) não são recoloridas. A causa de fundo continua nas folhas antigas (regra "HARD READABILITY FIX", que força texto creme dentro de `<main>`); o script contorna, não substitui uma revisão de CSS.
- `content-visibility: auto` foi desligado nas seções: com tamanhos estimados, as seções mudavam de altura ao rolar e os auditores (axe, Lighthouse) mediam o fundo errado.
- Datas: `python3 scripts/stamp_page_dates.py --date AAAA-MM-DD [páginas]` grava "Atualizado em" visível, `dateModified` no JSON-LD e `lastmod` no sitemap. `--check` lista páginas sem data.
- `llms.txt` (PT/EN/ES) é gerado por `scripts/apply_growth_p1_p2.py` a partir de `data/llms/<idioma>.md`; edite esses arquivos, não o `llms.txt` direto.
- Fatos padronizados: nota 4,8 no Google sem número de avaliações; "único restaurante do Parque Bondinho com vista direta para o Pão de Açúcar"; café da manhã à la carte; a reserva não inclui o ingresso do Bondinho.
- Relatório: `_audit_reports/nivel_a_2026-10-20.md`.

### A+ — 20/10/2026 (noite)

- 17/17 checagens. O formulário de eventos (LeoRangel22/main, PR #62) agora tem contraste AA e um aviso curto de privacidade com link; a política ganhou a seção "Formulário de eventos".
- Markdown para agentes de IA: `/pagina.md` e `Accept: text/markdown` (gerado por `scripts/build_markdown.py` no build e servido pela Function). Browsers continuam recebendo HTML.
- robots.txt com `Content-Signal: search=yes, ai-input=yes, ai-train=no`.
- Autoria: Embaixada Carioca (meta author, author/publisher no JSON-LD, endereço no rodapé).
- Imagens de 800 px para celular: rode `scripts/make_responsive_images.py` ao adicionar fotos.
- Chope: "2º lugar no Heineken Masters 2025", com link da Heineken.
- Sem `datePublished`: o histórico do repositório começa em 14/05/2026 e não há data real de publicação mais antiga.

### Design 2026 em todas as páginas — 20/10/2026

- As 70 páginas internas (PT/EN/ES, mais 404, offline e política de privacidade) passam a ser geradas por `scripts/build_pages_2026.py` a partir de `content/pages/<caminho>.html`: um bloco `<!--page {JSON} -->` com metadados, hero, fatos e FAQ, seguido do HTML das seções. Com a home e os 3 guias de visita, são 74 páginas no design 2026. Fica de fora só `formulario.html`, que redireciona para o formulário de eventos.
- CSS: 2 combinações, contra pelo menos 23 antes. A home usa `ec-home-2026.css`; todas as outras páginas usam `ec-home-2026.css` + `ec-pages-2026.css` + `ec-growth-links.css`. Para mudar o visual de todas as páginas, edite `ec-pages-2026.css` e suba `CSS_VERSION` no builder.
- Para editar uma página: altere o arquivo em `content/pages/` e rode `build_pages_2026.py <páginas>`, depois `apply_growth_p1_p2.py` e `stamp_page_dates.py --date AAAA-MM-DD <páginas>`. Não edite o HTML publicado à mão: o CI (`growth-p1-p2.yml`) roda `build_pages_2026.py --check` e `stamp_page_dates.py --check`.
- Conteúdo enxuto: fatos, preços (cardápio de 19/10/2026), FAQs e links mantidos. Removidos os blocos SEO repetidos e as alegações sem fonte: bylines de "especialistas", "melhor do Rio", "escolha número um", comparações nominais com concorrentes, depoimentos apresentados como avaliações, itens fora do cardápio e listas de "fontes editoriais".
- O JSON-LD é gerado de forma padronizada: um `@graph` com Restaurant, WebSite, WebPage, BreadcrumbList e FAQPage, além de Menu e MenuItem onde houver. Saíram os VideoObject inventados e os eventos anuais genéricos.
- As páginas passaram de 110–310 KB para 19–55 KB. axe 4.10, em 375 e 1440 px: 0 violações e nenhuma rolagem horizontal. Todos os links internos respondem 200.
- PRs: #39 (páginas principais), #40 (guias), #41 (restaurante e gastronomia) e o lote 4 (institucionais).

### Publicação pelo GitHub Actions — 20/10/2026

- A integração Git do Cloudflare Pages parou de publicar depois que o repositório foi transferido de `LeoRangel22` para a organização `Embaixada-Carioca`: o projeto continua ligado ao dono antigo ("internal issue with your Cloudflare Workers & Pages Git installation"). A produção ficou no commit `0a6764f` de 05/10/2026 até 20/10/2026.
- Desde 20/10/2026, cada push no `master` roda `.github/workflows/cloudflare-pages-deploy.yml`: build (`scripts/build_cloudflare_pages.py`), teste do roteador e `wrangler pages deploy` no projeto `embaixada-carioca`, com o mesmo domínio. O token fica no secret `CLOUDFLARE_API_TOKEN` (permissão Cloudflare Pages: Edit) e é validado antes do deploy.
- O app "Cloudflare Workers and Pages" foi instalado na organização, só neste repositório. O aviso da integração Git continua no painel do Cloudflare e não afeta o deploy pelo Actions.
- O workflow "Verify live site" não detectou a produção desatualizada; conferir o deploy pelo resultado do workflow de publicação.

### Lote de design interno — 09/09/2026

- Base responsiva e navegação compacta estendidas a 24 páginas comerciais/editoriais PT/EN/ES.
- Refino das aberturas de Cardápio e Café da Manhã, com fotos conferidas e textos localizados; preços e cards preservados.
- Menu móvel funcional, troca de idioma para página equivalente e topo sólido após rolagem.
- 144 cenários de páginas internas, 18 de homes e 48 verificações adicionais de conteúdo/rolagem aprovados localmente.
- Detalhes e limites: `_audit_reports/inner_design_rollout_2026-09-09.md`. Não equivale a certificação AAA nem revisão editorial completa do site.

### Lote de experiência de visita — 08/09/2026

- Homes PT/EN/ES usam composição responsiva em fluxo, sem o logo secundário sobre o texto e sem popup automático de WhatsApp.
- CTAs de cardápio e acesso apontam às páginas correspondentes no idioma da home; placeholders do rodapé foram substituídos por destinos úteis.
- Removidas horas fixas/estimativa sazonal imprecisa do pôr do sol. Mantidos os horários de funcionamento já informados.
- Prêmios contextualizados como feijoada da Academia da Cachaça servida por parceria formal. Removidas alegações amplas de exclusividade de serviço e de liderança em avaliações nas homes.
- Barra mobile de reserva redundante ocultada; navegação e idioma mobile restaurados nas homes.
- Instagram público confirma bloqueio de 18 anos. Origem da configuração ainda não verificada: não há sessão administrativa conectada; nenhuma configuração foi alterada.
- Os 12 alertas editoriais de paridade já existentes continuam no backlog. Estes testes não certificam acessibilidade AAA nem paridade editorial integral.

Ver relatório do lote em `_audit_reports/home_visit_experience_2026-09-08.md`.

| Camada | Estado atual |
|---|---|
| Hospedagem pública principal | Cloudflare Pages |
| Projeto Pages | `embaixada-carioca.pages.dev` |
| Plano Cloudflare | Free — suficiente para o uso atual |
| DNS de `www` | CNAME para o projeto Cloudflare Pages |
| Fonte de produção | GitHub, branch `master`, publicado pelo workflow `Cloudflare Pages deploy` (`.github/workflows/cloudflare-pages-deploy.yml`, secret `CLOUDFLARE_API_TOKEN`) |
| GitHub Pages | publicação secundária mantida; não é o destino canônico do DNS |

## Rede, redirecionamentos e segurança

Verificado ao vivo em 31/08/2026:

- `http://www.embaixadacarioca.com/...` responde `301` para HTTPS.
- `https://embaixadacarioca.com/` consolida em `https://www.embaixadacarioca.com/`.
- `.com.br`, com e sem `www`, responde `301` para o domínio `.com` canônico.
- `/index.html` responde `301` para `/`.
- aliases como `/cardapio` e `/eventos` respondem `301` para suas URLs `.html`.
- HSTS está ativo em fase gradual: `max-age=86400`.
- CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` e `Permissions-Policy` são entregues pelo Cloudflare.

O HSTS ainda não deve ser descrito como implantação definitiva com subdomínios/preload. A ampliação depende de monitoramento sem regressões.

## Indexação

- `sitemap.xml`: 72 URLs canônicas no inventário de 22/10/2026.
- Sitemap reenviado ao Search Console em 27/08/2026 e processado com 97 páginas.
- URLs alternativas e aliases não devem ser solicitados para indexação; o destino é sempre a canonical.
- O próximo passo é acompanhar recrawl, indexação e CTR, não reenviar repetidamente sem mudança material.

## Idiomas e conteúdo

- Português, inglês e espanhol publicados.
- Hreflang PT/EN/ES/x-default: PASS, nota mínima 100.
- Todas as páginas PT do escopo i18n possuem contrapartes EN e ES.
- Permanecem 12 diferenças editoriais advisory de títulos/seções que exigem revisão humana, sem impedir a validação estrutural.
- Cardápio: 12 seções e 149 itens por idioma na última auditoria de paridade.

## Entidade e fatos oficiais

- Diferencial: único restaurante do Parque Bondinho com vista direta para o Pão de Açúcar (frase oficial; não usar variantes sem "com vista direta", como "único restaurante dentro do parque" ou "único almoço").
- Avaliação Google: nota 4,8 (sem número de avaliações no site, que fica desatualizado; decisão de 20/10/2026).
- Instagram: 84 mil seguidores.
- Melhor Feijoada do Brasil: Academia da Cachaça, Prazeres da Mesa, 2017.
- Melhor Feijoada do Rio: Veja Rio Comer & Beber, 2025/2026.
- A feijoada da Academia da Cachaça é servida na Embaixada Carioca por parceria formal.
- Embaixada Carioca e Cantina do MAM têm os mesmos sócios, conforme confirmação do responsável.

## JSON-LD

- Guard de rating/review: PASS em 110 arquivos, 0 ocorrências proibidas.
- Guard de chaves duplicadas: PASS em 110 arquivos, 0 chaves duplicadas.
- Não usar `Review`, `Rating`, `AggregateRating` ou campos derivados no JSON-LD.
- Prova social pode existir visualmente, sem marcação estruturada de avaliações.

## Analytics e conversão

- Instrumentação de funil implantada em 24/08/2026.
- `ec_event_lead_outbound` marcado como evento principal no GA4 em 27/08/2026.
- Cliques de navegação e microinterações devem continuar como eventos diagnósticos, não como conversões principais.
- Reserva concluída na Tagme ainda precisa de integração ou reconciliação confiável com o GA4.
- Formulário de eventos deve ser medido por etapas antes de uma troca de canal ou reconstrução.

## SEO em medição

O lote de CTR de 27/08/2026 atualizou:

- `almoco.html` para consultas de “almoço no Pão de Açúcar”;
- `en/where-to-eat-near-sugarloaf.html`;
- `es/donde-comer-cerca-del-pan-de-azucar.html`.

Os títulos do cluster restaurante/Bondinho também foram estabilizados. Não reescrever antes de:

- leitura direcional em 10/09/2026 (14 dias);
- decisão com janela consolidada em 24/09/2026 (28 dias).

## Governança de automações

Inventário histórico de workflows (anterior ao deploy Actions de 20/10 e aos gates de 22/10; não representa a lista ativa atual):

1. Pages build and deployment.
2. Verify live site.
3. Super site standards SEO audit.
4. Schema JSON-LD CI gate.
5. Accessibility CI.
6. Hreflang Validation.
7. i18n Sync Validation.

Desativados: 30 workflows legados de correção automática ou execução manual perigosa. Não reativar em lote.

## Próximas ações de alto impacto

1. Monitorar o HSTS curto e ampliar gradualmente somente após validar todos os hosts HTTPS.
2. Medir o lote de CTR nas datas previstas, usando página + consulta + país/idioma.
3. Fechar a medição de reservas concluídas da Tagme.
4. Medir o funil de eventos antes de decidir novo formulário ou novo canal de envio.
5. Publicar capacidades, faixas de investimento e calendário apenas com dados comerciais aprovados.
6. Continuar a revisão editorial nativa das 12 diferenças PT/EN/ES.
7. Monitorar respostas 5xx/erros transitórios no Cloudflare.

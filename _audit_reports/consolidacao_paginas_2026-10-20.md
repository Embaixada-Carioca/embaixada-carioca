# Consolidação de páginas por variação de busca — 20/10/2026

Decisão do responsável em 20/10/2026, com base no Search Console (propriedade `sc-domain:embaixadacarioca.com`, últimos 3 meses, Pesquisa na Web, consultado em 20/10/2026). Total do período: 3,67 mil cliques e 191 mil impressões.

## Redirecionamentos 301

Cada URL redireciona para a página principal do mesmo idioma, em `functions/[[path]].js` (`LEGACY_REDIRECTS`). Os arquivos HTML continuam no repositório, então a mudança é reversível removendo as linhas do mapa e devolvendo as URLs ao sitemap.

Grupo A: mesma intenção de uma página principal e pouco tráfego.

| De | Para | Cliques | Impressões |
|---|---|---:|---:|
| feijoada-morro-da-urca.html | feijoada.html | 1 | 116 |
| feijoada-com-vista-rio-de-janeiro.html (+ EN, ES) | feijoada.html de cada idioma | 4 / 0 / 2 | 69 / 20 / 299 |
| almoco-morro-da-urca.html (+ EN, ES) | almoco.html de cada idioma | 0 / 2 / 0 | 78 / 150 / 17 |
| cafe-da-manha-pao-de-acucar.html (+ EN, ES) | cafe-da-manha.html de cada idioma | 1 / 6 / 1 | 86 / 234 / 8 |
| cafe-da-manha-com-vista-rio-de-janeiro.html (só PT) | cafe-da-manha.html | 2 | 808 |
| por-do-sol-morro-da-urca.html (+ EN, ES) | entardecer.html · en/sunset.html · es/atardecer.html | 0 / 3 / 0 | 29 / 85 / 41 |
| sunset-por-do-sol-rio-de-janeiro.html (+ EN, ES) | entardecer.html · en/sunset.html · es/atardecer.html | 0 | 0 |
| restaurantes-romanticos-rio-de-janeiro.html | entardecer.html | 0 | 0 |
| restaurante-com-vista-rio-de-janeiro.html (+ EN, ES) | / · /en/ · /es/ | 0 / 1 / 0 | 56 / 80 / 29 |

Grupo B: páginas do mapa de palavras-ouro de agosto ou com algum tráfego.

| De | Para | Cliques | Impressões |
|---|---|---:|---:|
| restaurante-pao-de-acucar.html (+ en/restaurant-at-sugarloaf, es/restaurante-pan-de-azucar) | onde-comer de cada idioma | 2 / 0 / 0 | 156 / 87 / 33 |
| restaurantes-perto-do-pao-de-acucar.html (+ en/restaurants-near-sugarloaf-mountain, es/restaurantes-cerca-del-pan-de-azucar) | onde-comer de cada idioma | 3 / 2 / 0 | 121 / 81 / 7 |
| parque-bondinho-pao-de-acucar.html (+ en/sugarloaf-cable-car-park, es/parque-bondinho-pan-de-azucar) | parque-bondinho de cada idioma | 24 / 2 / 8 | 4.622 / 164 / 1.785 |

Referência das páginas que recebem o tráfego (cliques / impressões): cafe-da-manha 438 / 9.885; onde-comer-no-pao-de-acucar 39 / 3.460; feijoada 30 / 2.495; almoco 23 / 2.464; parque-bondinho 66 / 46.438; entardecer 4 / 297.

Mantidas como páginas próprias: restaurante-morro-da-urca, restaurante-bondinho-pao-de-acucar (a versão ES é a página de restaurante mais forte do idioma), gastronomia-carioca, caipirinha-com-vista-rio, en/breakfast-with-a-view-rio-de-janeiro e es/desayuno-con-vista-rio-de-janeiro.

## Ajustes relacionados

- `sitemap.xml`: 102 → 75 URLs. As alternates pt-BR e x-default de en/breakfast-with-a-view e es/desayuno-con-vista apontavam para cafe-da-manha-com-vista-rio-de-janeiro.html e foram removidas; o par EN↔ES foi mantido.
- Links internos: 16 links em 13 páginas foram reapontados para o destino final ou removidos, quando passariam a apontar para a própria página ou repetiriam um link do mesmo bloco. A seção "Feijoada no Morro da Urca" de feijoada.html, que só linkava a página incorporada, foi removida.
- Endereços sem `.html` das páginas incorporadas redirecionam em um salto só.
- `validate_restaurant_search_cluster.py`: removidas as três páginas "restaurantes perto" consolidadas; as 6 falhas restantes já existiam antes deste lote.
- `test_growth_router.mjs`: verifica os 30 redirecionamentos, sem cadeia, com e sem `.html`.

## Search Console (20/10/2026)

- Indexação: 100 páginas indexadas e 27 não indexadas. Em "Não encontrado (404)": `https://www.embaixadacarioca.com/` (rastreada em 29/07/2026), `/en/como-chegar.html` e `/inquiry-services-page`. A home consta hoje como indexada na Inspeção de URL. O 404 da home é coerente com a falha de revalidação corrigida em `69403cd`.
- O relatório de desempenho registra `http://www.embaixadacarioca.com/` com 581 cliques e 31 mil impressões, além da versão https.

## Depois da publicação

1. Reenviar `sitemap.xml` no Search Console.
2. Pedir validação de "Não encontrado (404)" e de "Página com redirecionamento".
3. Comparar 28 dias antes e depois por página de destino: cafe-da-manha, feijoada, almoco, entardecer, onde-comer e parque-bondinho.

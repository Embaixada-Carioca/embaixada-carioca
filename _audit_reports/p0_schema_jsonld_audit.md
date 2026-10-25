# P0 Schema JSON-LD Audit

Status geral: **PASS**
Score mínimo: **100**

## Critérios
- Bloco `<script type="application/ld+json">` válido.
- Tipos mínimos: Restaurant, FAQPage, Menu, BreadcrumbList, WebSite e WebPage.
- Proibido usar `aggregateRating`, `ratingValue`, `reviewCount`, `ratingCount`, `bestRating` ou `worstRating` no JSON-LD.
- O rating do Google pode aparecer no texto visível, mas não no schema estruturado.
- Score mínimo: 90.

## Resultados
- `index.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, Menu, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `en/index.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `es/index.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `almoco.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `en/almoco.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `es/almoco.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `cafe-da-manha.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `en/cafe-da-manha.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `es/cafe-da-manha.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `cardapio.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, Menu, MenuItem, MenuSection, Offer, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `restaurante-morro-da-urca.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `eventos.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `en/eventos.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `es/eventos.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `guia-do-rio.html` — PASS — score 100 — blocos válidos 1
  - Encontrado: Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, OpeningHoursSpecification, PostalAddress, Question, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite
- `restaurantes-romanticos-rio-de-janeiro.html` — PASS — score 100 — blocos válidos 2
  - Encontrado: AdministrativeArea, Answer, BreadcrumbList, City, FAQPage, GeoCoordinates, ListItem, Neighborhood, OpeningHoursSpecification, PostalAddress, Question, ReserveAction, Restaurant, SpeakableSpecification, TouristAttraction, WebPage, WebSite

const LEGACY_REDIRECTS = new Map([
  ["/en", "/en/"],
  ["/es", "/es/"],
  ["/cafe-manha.html", "/cafe-da-manha.html"],
  ["/pao-bondinho.html", "/parque-bondinho.html"],
  ["/es/donde-comer-cerca-al-pan-de-azucar.html", "/es/donde-comer-cerca-del-pan-de-azucar.html"],
  ["/es/donde-comer-cerca-de-pan-de-azucar", "/es/donde-comer-cerca-del-pan-de-azucar.html"],
  ["/es/o-que-fazer-depois-do-bondinho-pao-de-acucar/", "/es/o-que-fazer-depois-do-bondinho-pao-de-acucar.html"],
  ["/es/como-chegar.html", "/es/como-llegar.html"],
  ["/general-3", "/"],
  ["/inquiry-services-page", "/eventos.html"],
  ["/caf%C3%A9-da-manh%C3%A3-com-a-melhor-vista-do-rio", "/cafe-da-manha-com-vista-rio-de-janeiro.html"],
  ["/en/como-chegar.html", "/en/how-to-get-there.html"],
  ["/restaurante-urca.html", "/restaurante-morro-da-urca.html"],
  // Consolidação de 20/10/2026: páginas com a mesma intenção de uma página principal
  // (Search Console, jul–out/2026). Detalhes em _audit_reports/consolidacao_paginas_2026-10-20.md.
  ["/feijoada-morro-da-urca.html", "/feijoada.html"],
  ["/feijoada-com-vista-rio-de-janeiro.html", "/feijoada.html"],
  ["/almoco-morro-da-urca.html", "/almoco.html"],
  ["/cafe-da-manha-pao-de-acucar.html", "/cafe-da-manha.html"],
  ["/cafe-da-manha-com-vista-rio-de-janeiro.html", "/cafe-da-manha.html"],
  ["/por-do-sol-morro-da-urca.html", "/entardecer.html"],
  ["/sunset-por-do-sol-rio-de-janeiro.html", "/entardecer.html"],
  ["/restaurantes-romanticos-rio-de-janeiro.html", "/entardecer.html"],
  ["/restaurante-com-vista-rio-de-janeiro.html", "/"],
  ["/restaurante-pao-de-acucar.html", "/onde-comer-no-pao-de-acucar.html"],
  ["/restaurantes-perto-do-pao-de-acucar.html", "/onde-comer-no-pao-de-acucar.html"],
  ["/parque-bondinho-pao-de-acucar.html", "/parque-bondinho.html"],
  ["/en/feijoada-com-vista-rio-de-janeiro.html", "/en/feijoada.html"],
  ["/en/almoco-morro-da-urca.html", "/en/almoco.html"],
  ["/en/cafe-da-manha-pao-de-acucar.html", "/en/cafe-da-manha.html"],
  ["/en/por-do-sol-morro-da-urca.html", "/en/sunset.html"],
  ["/en/sunset-por-do-sol-rio-de-janeiro.html", "/en/sunset.html"],
  ["/en/restaurante-com-vista-rio-de-janeiro.html", "/en/"],
  ["/en/restaurant-at-sugarloaf.html", "/en/where-to-eat-near-sugarloaf.html"],
  ["/en/restaurants-near-sugarloaf-mountain.html", "/en/where-to-eat-near-sugarloaf.html"],
  ["/en/sugarloaf-cable-car-park.html", "/en/parque-bondinho.html"],
  ["/es/feijoada-com-vista-rio-de-janeiro.html", "/es/feijoada.html"],
  ["/es/almoco-morro-da-urca.html", "/es/almoco.html"],
  ["/es/cafe-da-manha-pao-de-acucar.html", "/es/cafe-da-manha.html"],
  ["/es/por-do-sol-morro-da-urca.html", "/es/atardecer.html"],
  ["/es/sunset-por-do-sol-rio-de-janeiro.html", "/es/atardecer.html"],
  ["/es/restaurante-com-vista-rio-de-janeiro.html", "/es/"],
  ["/es/restaurante-pan-de-azucar.html", "/es/donde-comer-cerca-del-pan-de-azucar.html"],
  ["/es/restaurantes-cerca-del-pan-de-azucar.html", "/es/donde-comer-cerca-del-pan-de-azucar.html"],
  ["/es/parque-bondinho-pan-de-azucar.html", "/es/parque-bondinho.html"],
]);

function redirect(requestUrl, destination) {
  const target = new URL(destination, requestUrl);
  target.search = new URL(requestUrl).search;
  return new Response(null, {
    status: 301,
    headers: {
      Location: target.pathname + target.search,
      "Cache-Control": "public, max-age=3600",
    },
  });
}

// Only cache-validation headers reach the asset lookup. Forwarding the whole
// browser request made the lookup answer 304 (If-None-Match) or 206 (Range),
// which was treated as "page not found" and became an empty 404: returning
// visitors and recrawls got an error instead of the page.
const VALIDATION_HEADERS = ["If-None-Match", "If-Modified-Since"];

async function storedHtml(context, publicPath, { conditional = true } = {}) {
  const assetPath = `/_html${publicPath}.txt`;
  const assetUrl = new URL(assetPath, context.request.url);
  const lookupHeaders = new Headers();
  if (conditional) {
    for (const name of VALIDATION_HEADERS) {
      const value = context.request.headers.get(name);
      if (value) lookupHeaders.set(name, value);
    }
  }
  const assetRequest = new Request(assetUrl, { method: "GET", headers: lookupHeaders });
  const response = await context.env.ASSETS.fetch(assetRequest);

  if (response.status === 304) {
    const headers = new Headers(response.headers);
    headers.set("X-Canonical-HTML", "preserved");
    return new Response(null, { status: 304, headers });
  }

  if (response.status !== 200) return null;

  const headers = new Headers(response.headers);
  headers.set("Content-Type", "text/html; charset=UTF-8");
  headers.set("X-Canonical-HTML", "preserved");
  return new Response(context.request.method === "HEAD" ? null : response.body, {
    status: 200,
    headers,
  });
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname;

  // Fixed destination: do not forward arbitrary query strings or contact data.
  if (path === "/formulario" || path === "/formulario.html") {
    return new Response(null, {
      status: 301,
      headers: {
        Location: "https://leorangel22.github.io/main/formulario.html?utm_source=embaixadacarioca&utm_medium=website&utm_campaign=eventos&utm_content=formulario",
        "Cache-Control": "public, max-age=3600",
      },
    });
  }

  if (path.startsWith("/_html/")) {
    return new Response("Not found", { status: 404 });
  }

  if (LEGACY_REDIRECTS.has(path)) {
    return redirect(context.request.url, LEGACY_REDIRECTS.get(path));
  }

  if (path === "/") {
    return (await storedHtml(context, "/index.html")) || context.next();
  }

  if (path === "/en/" || path === "/es/") {
    return (await storedHtml(context, `${path}index.html`)) || context.next();
  }

  if (path.endsWith("/index.html")) {
    return redirect(context.request.url, path.slice(0, -"index.html".length));
  }

  if (path.endsWith(".html")) {
    return (await storedHtml(context, path)) || context.next();
  }

  if (!path.endsWith("/") && !path.split("/").pop().includes(".")) {
    const canonicalPath = `${path}.html`;
    if (LEGACY_REDIRECTS.has(canonicalPath)) {
      return redirect(context.request.url, LEGACY_REDIRECTS.get(canonicalPath));
    }
    if (await storedHtml(context, canonicalPath, { conditional: false })) {
      return redirect(context.request.url, canonicalPath);
    }
  }

  const fallback = await context.next();
  if (fallback.status === 404 && wantsHtml(context.request)) {
    const page = await storedHtml(context, "/404.html", { conditional: false });
    if (page) {
      const headers = new Headers(page.headers);
      headers.set("Cache-Control", "no-store");
      headers.delete("ETag");
      return new Response(context.request.method === "HEAD" ? null : page.body, { status: 404, headers });
    }
  }
  return fallback;
}

function wantsHtml(request) {
  if (request.method !== "GET" && request.method !== "HEAD") return false;
  return (request.headers.get("Accept") || "").includes("text/html");
}
